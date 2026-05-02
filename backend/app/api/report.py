"""
Report API路由
提供模拟报告生成、获取、对话等接口
"""

import os
import traceback
import threading
from flask import request, jsonify, send_file

from . import report_bp
from ..config import Config
from ..services.report_agent import ReportAgent, ReportManager, ReportStatus
from ..services.simulation_manager import SimulationManager
from ..models.project import ProjectManager
from ..models.task import TaskManager, TaskStatus
from ..utils.logger import get_logger
from ..utils.locale import t, get_locale, set_locale

logger = get_logger('mirofish.api.report')
dd_progress_store: dict = {}


# ============== 报告生成接口 ==============

@report_bp.route('/generate', methods=['POST'])
def generate_report():
    """
    生成模拟分析报告（异步任务）
    
    这是一个耗时操作，接口会立即返回task_id，
    使用 GET /api/report/generate/status 查询进度
    
    请求（JSON）：
        {
            "simulation_id": "sim_xxxx",    // 必填，模拟ID
            "force_regenerate": false        // 可选，强制重新生成
        }
    
    返回：
        {
            "success": true,
            "data": {
                "simulation_id": "sim_xxxx",
                "task_id": "task_xxxx",
                "status": "generating",
                "message": "报告生成任务已启动"
            }
        }
    """
    try:
        data = request.get_json() or {}
        
        simulation_id = data.get('simulation_id')
        if not simulation_id:
            return jsonify({
                "success": False,
                "error": t('api.requireSimulationId')
            }), 400

        force_regenerate = data.get('force_regenerate', False)
        
        # 获取模拟信息
        manager = SimulationManager()
        state = manager.get_simulation(simulation_id)
        
        if not state:
            return jsonify({
                "success": False,
                "error": t('api.simulationNotFound', id=simulation_id)
            }), 404

        # 检查是否已有报告
        if not force_regenerate:
            existing_report = ReportManager.get_report_by_simulation(simulation_id)
            if existing_report and existing_report.status == ReportStatus.COMPLETED:
                return jsonify({
                    "success": True,
                    "data": {
                        "simulation_id": simulation_id,
                        "report_id": existing_report.report_id,
                        "status": "completed",
                        "message": t('api.reportAlreadyExists'),
                        "already_generated": True
                    }
                })
        
        # 获取项目信息
        project = ProjectManager.get_project(state.project_id)
        if not project:
            return jsonify({
                "success": False,
                "error": t('api.projectNotFound', id=state.project_id)
            }), 404
        
        graph_id = state.graph_id or project.graph_id
        if not graph_id:
            return jsonify({
                "success": False,
                "error": t('api.missingGraphIdEnsure')
            }), 400
        
        simulation_requirement = project.simulation_requirement
        if not simulation_requirement:
            return jsonify({
                "success": False,
                "error": t('api.missingSimRequirement')
            }), 400
        
        # 提前生成 report_id，以便立即返回给前端
        import uuid
        report_id = f"report_{uuid.uuid4().hex[:12]}"
        
        # 创建异步任务
        task_manager = TaskManager()
        task_id = task_manager.create_task(
            task_type="report_generate",
            metadata={
                "simulation_id": simulation_id,
                "graph_id": graph_id,
                "report_id": report_id
            }
        )
        
        # Capture locale before spawning background thread
        current_locale = get_locale()

        # 定义后台任务
        def run_generate():
            set_locale(current_locale)
            try:
                task_manager.update_task(
                    task_id,
                    progress=int((q_current / 148) * 100),
                    message=f"DD Q{q_current}/148 — {domain['name']}"
                )
                _time.sleep(1.5)
                
                # 创建Report Agent
                agent = ReportAgent(
                    graph_id=graph_id,
                    simulation_id=simulation_id,
                    simulation_requirement=simulation_requirement
                )
                
                # 进度回调
                def progress_callback(stage, progress, message):
                    task_manager.update_task(
                        task_id,
                        progress=progress,
                        message=f"[{stage}] {message}"
                    )
                
                # 生成报告（传入预先生成的 report_id）
                report = agent.generate_report(
                    progress_callback=progress_callback,
                    report_id=report_id
                )
                
                # 保存报告
                ReportManager.save_report(report)
                
                if report.status == ReportStatus.COMPLETED:
                    task_manager.complete_task(
                        task_id,
                        result={
                            "report_id": report.report_id,
                            "simulation_id": simulation_id,
                            "status": "completed"
                        }
                    )
                else:
                    task_manager.fail_task(task_id, report.error or t('api.reportGenerateFailed'))
                
            except Exception as e:
                logger.error(f"报告生成失败: {str(e)}")
                task_manager.fail_task(task_id, str(e))
        
        # 启动后台线程
        thread = threading.Thread(target=run_generate, daemon=True)
        thread.start()
        
        return jsonify({
            "success": True,
            "data": {
                "simulation_id": simulation_id,
                "report_id": report_id,
                "task_id": task_id,
                "status": "generating",
                "message": t('api.reportGenerateStarted'),
                "already_generated": False
            }
        })
        
    except Exception as e:
        logger.error(f"启动报告生成任务失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500


@report_bp.route('/generate/status', methods=['POST'])
def get_generate_status():
    """
    查询报告生成任务进度
    
    请求（JSON）：
        {
            "task_id": "task_xxxx",         // 可选，generate返回的task_id
            "simulation_id": "sim_xxxx"     // 可选，模拟ID
        }
    
    返回：
        {
            "success": true,
            "data": {
                "task_id": "task_xxxx",
                "status": "processing|completed|failed",
                "progress": 45,
                "message": "..."
            }
        }
    """
    try:
        data = request.get_json() or {}
        
        task_id = data.get('task_id')
        simulation_id = data.get('simulation_id')
        
        # 如果提供了simulation_id，先检查是否已有完成的报告
        if simulation_id:
            existing_report = ReportManager.get_report_by_simulation(simulation_id)
            if existing_report and existing_report.status == ReportStatus.COMPLETED:
                return jsonify({
                    "success": True,
                    "data": {
                        "simulation_id": simulation_id,
                        "report_id": existing_report.report_id,
                        "status": "completed",
                        "progress": 100,
                        "message": t('api.reportGenerated'),
                        "already_completed": True
                    }
                })
        
        if not task_id:
            return jsonify({
                "success": False,
                "error": t('api.requireTaskOrSimId')
            }), 400
        
        task_manager = TaskManager()
        task = task_manager.get_task(task_id)
        
        if not task:
            return jsonify({
                "success": False,
                "error": t('api.taskNotFound', id=task_id)
            }), 404
        
        return jsonify({
            "success": True,
            "data": task.to_dict()
        })
        
    except Exception as e:
        logger.error(f"查询任务状态失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ============== 报告获取接口 ==============

@report_bp.route('/<report_id>', methods=['GET'])
def get_report(report_id: str):
    """
    获取报告详情
    
    返回：
        {
            "success": true,
            "data": {
                "report_id": "report_xxxx",
                "simulation_id": "sim_xxxx",
                "status": "completed",
                "outline": {...},
                "markdown_content": "...",
                "created_at": "...",
                "completed_at": "..."
            }
        }
    """
    try:
        report = ReportManager.get_report(report_id)
        
        if not report:
            return jsonify({
                "success": False,
                "error": t('api.reportNotFound', id=report_id)
            }), 404
        
        return jsonify({
            "success": True,
            "data": report.to_dict()
        })
        
    except Exception as e:
        logger.error(f"获取报告失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500


@report_bp.route('/by-simulation/<simulation_id>', methods=['GET'])
def get_report_by_simulation(simulation_id: str):
    """
    根据模拟ID获取报告
    
    返回：
        {
            "success": true,
            "data": {
                "report_id": "report_xxxx",
                ...
            }
        }
    """
    try:
        report = ReportManager.get_report_by_simulation(simulation_id)
        
        if not report:
            return jsonify({
                "success": False,
                "error": t('api.noReportForSim', id=simulation_id),
                "has_report": False
            }), 404
        
        return jsonify({
            "success": True,
            "data": report.to_dict(),
            "has_report": True
        })
        
    except Exception as e:
        logger.error(f"获取报告失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500


@report_bp.route('/list', methods=['GET'])
def list_reports():
    """
    列出所有报告
    
    Query参数：
        simulation_id: 按模拟ID过滤（可选）
        limit: 返回数量限制（默认50）
    
    返回：
        {
            "success": true,
            "data": [...],
            "count": 10
        }
    """
    try:
        simulation_id = request.args.get('simulation_id')
        limit = request.args.get('limit', 50, type=int)
        
        reports = ReportManager.list_reports(
            simulation_id=simulation_id,
            limit=limit
        )
        
        return jsonify({
            "success": True,
            "data": [r.to_dict() for r in reports],
            "count": len(reports)
        })
        
    except Exception as e:
        logger.error(f"列出报告失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500


@report_bp.route('/<report_id>/download', methods=['GET'])
def download_report(report_id: str):
    """
    下载报告（Markdown格式）
    
    返回Markdown文件
    """
    try:
        report = ReportManager.get_report(report_id)
        
        if not report:
            return jsonify({
                "success": False,
                "error": t('api.reportNotFound', id=report_id)
            }), 404
        
        md_path = ReportManager._get_report_markdown_path(report_id)
        
        if not os.path.exists(md_path):
            # 如果MD文件不存在，生成一个临时文件
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
                f.write(report.markdown_content)
                temp_path = f.name
            
            return send_file(
                temp_path,
                as_attachment=True,
                download_name=f"{report_id}.md"
            )
        
        return send_file(
            md_path,
            as_attachment=True,
            download_name=f"{report_id}.md"
        )
        
    except Exception as e:
        logger.error(f"下载报告失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500


@report_bp.route('/<report_id>', methods=['DELETE'])
def delete_report(report_id: str):
    """删除报告"""
    try:
        success = ReportManager.delete_report(report_id)
        
        if not success:
            return jsonify({
                "success": False,
                "error": t('api.reportNotFound', id=report_id)
            }), 404
        
        return jsonify({
            "success": True,
            "message": t('api.reportDeleted', id=report_id)
        })
        
    except Exception as e:
        logger.error(f"删除报告失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500


# ============== Report Agent对话接口 ==============

@report_bp.route('/chat', methods=['POST'])
def chat_with_report_agent():
    """
    与Report Agent对话
    
    Report Agent可以在对话中自主调用检索工具来回答问题
    
    请求（JSON）：
        {
            "simulation_id": "sim_xxxx",        // 必填，模拟ID
            "message": "请解释一下舆情走向",    // 必填，用户消息
            "chat_history": [                   // 可选，对话历史
                {"role": "user", "content": "..."},
                {"role": "assistant", "content": "..."}
            ]
        }
    
    返回：
        {
            "success": true,
            "data": {
                "response": "Agent回复...",
                "tool_calls": [调用的工具列表],
                "sources": [信息来源]
            }
        }
    """
    try:
        data = request.get_json() or {}
        
        simulation_id = data.get('simulation_id')
        message = data.get('message')
        chat_history = data.get('chat_history', [])
        
        if not simulation_id:
            return jsonify({
                "success": False,
                "error": t('api.requireSimulationId')
            }), 400

        if not message:
            return jsonify({
                "success": False,
                "error": t('api.requireMessage')
            }), 400
        
        # 获取模拟和项目信息
        manager = SimulationManager()
        state = manager.get_simulation(simulation_id)
        
        if not state:
            return jsonify({
                "success": False,
                "error": t('api.simulationNotFound', id=simulation_id)
            }), 404

        project = ProjectManager.get_project(state.project_id)
        if not project:
            return jsonify({
                "success": False,
                "error": t('api.projectNotFound', id=state.project_id)
            }), 404
        
        graph_id = state.graph_id or project.graph_id
        if not graph_id:
            return jsonify({
                "success": False,
                "error": t('api.missingGraphId')
            }), 400
        
        simulation_requirement = project.simulation_requirement or ""
        
        # 创建Agent并进行对话
        agent = ReportAgent(
            graph_id=graph_id,
            simulation_id=simulation_id,
            simulation_requirement=simulation_requirement
        )
        
        result = agent.chat(message=message, chat_history=chat_history)
        
        return jsonify({
            "success": True,
            "data": result
        })
        
    except Exception as e:
        logger.error(f"对话失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500


# ============== 报告进度与分章节接口 ==============

@report_bp.route('/<report_id>/progress', methods=['GET'])
def get_report_progress(report_id: str):
    """
    获取报告生成进度（实时）
    
    返回：
        {
            "success": true,
            "data": {
                "status": "generating",
                "progress": 45,
                "message": "正在生成章节: 关键发现",
                "current_section": "关键发现",
                "completed_sections": ["执行摘要", "模拟背景"],
                "updated_at": "2025-12-09T..."
            }
        }
    """
    try:
        progress = ReportManager.get_progress(report_id)
        
        if not progress:
            return jsonify({
                "success": False,
                "error": t('api.reportProgressNotAvail', id=report_id)
            }), 404
        
        return jsonify({
            "success": True,
            "data": progress
        })
        
    except Exception as e:
        logger.error(f"获取报告进度失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500


@report_bp.route('/<report_id>/sections', methods=['GET'])
def get_report_sections(report_id: str):
    """
    获取已生成的章节列表（分章节输出）
    
    前端可以轮询此接口获取已生成的章节内容，无需等待整个报告完成
    
    返回：
        {
            "success": true,
            "data": {
                "report_id": "report_xxxx",
                "sections": [
                    {
                        "filename": "section_01.md",
                        "section_index": 1,
                        "content": "## 执行摘要\\n\\n..."
                    },
                    ...
                ],
                "total_sections": 3,
                "is_complete": false
            }
        }
    """
    try:
        sections = ReportManager.get_generated_sections(report_id)
        
        # 获取报告状态
        report = ReportManager.get_report(report_id)
        is_complete = report is not None and report.status == ReportStatus.COMPLETED
        
        return jsonify({
            "success": True,
            "data": {
                "report_id": report_id,
                "sections": sections,
                "total_sections": len(sections),
                "is_complete": is_complete
            }
        })
        
    except Exception as e:
        logger.error(f"获取章节列表失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500


@report_bp.route('/<report_id>/section/<int:section_index>', methods=['GET'])
def get_single_section(report_id: str, section_index: int):
    """
    获取单个章节内容
    
    返回：
        {
            "success": true,
            "data": {
                "filename": "section_01.md",
                "content": "## 执行摘要\\n\\n..."
            }
        }
    """
    try:
        section_path = ReportManager._get_section_path(report_id, section_index)
        
        if not os.path.exists(section_path):
            return jsonify({
                "success": False,
                "error": t('api.sectionNotFound', index=f"{section_index:02d}")
            }), 404
        
        with open(section_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return jsonify({
            "success": True,
            "data": {
                "filename": f"section_{section_index:02d}.md",
                "section_index": section_index,
                "content": content
            }
        })
        
    except Exception as e:
        logger.error(f"获取章节内容失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500


# ============== 报告状态检查接口 ==============

@report_bp.route('/check/<simulation_id>', methods=['GET'])
def check_report_status(simulation_id: str):
    """
    检查模拟是否有报告，以及报告状态
    
    用于前端判断是否解锁Interview功能
    
    返回：
        {
            "success": true,
            "data": {
                "simulation_id": "sim_xxxx",
                "has_report": true,
                "report_status": "completed",
                "report_id": "report_xxxx",
                "interview_unlocked": true
            }
        }
    """
    try:
        report = ReportManager.get_report_by_simulation(simulation_id)
        
        has_report = report is not None
        report_status = report.status.value if report else None
        report_id = report.report_id if report else None
        
        # 只有报告完成后才解锁interview
        interview_unlocked = has_report and report.status == ReportStatus.COMPLETED
        
        return jsonify({
            "success": True,
            "data": {
                "simulation_id": simulation_id,
                "has_report": has_report,
                "report_status": report_status,
                "report_id": report_id,
                "interview_unlocked": interview_unlocked
            }
        })
        
    except Exception as e:
        logger.error(f"检查报告状态失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500


# ============== Agent 日志接口 ==============

@report_bp.route('/<report_id>/agent-log', methods=['GET'])
def get_agent_log(report_id: str):
    """
    获取 Report Agent 的详细执行日志
    
    实时获取报告生成过程中的每一步动作，包括：
    - 报告开始、规划开始/完成
    - 每个章节的开始、工具调用、LLM响应、完成
    - 报告完成或失败
    
    Query参数：
        from_line: 从第几行开始读取（可选，默认0，用于增量获取）
    
    返回：
        {
            "success": true,
            "data": {
                "logs": [
                    {
                        "timestamp": "2025-12-13T...",
                        "elapsed_seconds": 12.5,
                        "report_id": "report_xxxx",
                        "action": "tool_call",
                        "stage": "generating",
                        "section_title": "执行摘要",
                        "section_index": 1,
                        "details": {
                            "tool_name": "insight_forge",
                            "parameters": {...},
                            ...
                        }
                    },
                    ...
                ],
                "total_lines": 25,
                "from_line": 0,
                "has_more": false
            }
        }
    """
    try:
        from_line = request.args.get('from_line', 0, type=int)
        
        log_data = ReportManager.get_agent_log(report_id, from_line=from_line)
        
        return jsonify({
            "success": True,
            "data": log_data
        })
        
    except Exception as e:
        logger.error(f"获取Agent日志失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500


@report_bp.route('/<report_id>/agent-log/stream', methods=['GET'])
def stream_agent_log(report_id: str):
    """
    获取完整的 Agent 日志（一次性获取全部）
    
    返回：
        {
            "success": true,
            "data": {
                "logs": [...],
                "count": 25
            }
        }
    """
    try:
        logs = ReportManager.get_agent_log_stream(report_id)
        
        return jsonify({
            "success": True,
            "data": {
                "logs": logs,
                "count": len(logs)
            }
        })
        
    except Exception as e:
        logger.error(f"获取Agent日志失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500


# ============== 控制台日志接口 ==============

@report_bp.route('/<report_id>/console-log', methods=['GET'])
def get_console_log(report_id: str):
    """
    获取 Report Agent 的控制台输出日志
    
    实时获取报告生成过程中的控制台输出（INFO、WARNING等），
    这与 agent-log 接口返回的结构化 JSON 日志不同，
    是纯文本格式的控制台风格日志。
    
    Query参数：
        from_line: 从第几行开始读取（可选，默认0，用于增量获取）
    
    返回：
        {
            "success": true,
            "data": {
                "logs": [
                    "[19:46:14] INFO: 搜索完成: 找到 15 条相关事实",
                    "[19:46:14] INFO: 图谱搜索: graph_id=xxx, query=...",
                    ...
                ],
                "total_lines": 100,
                "from_line": 0,
                "has_more": false
            }
        }
    """
    try:
        from_line = request.args.get('from_line', 0, type=int)
        
        log_data = ReportManager.get_console_log(report_id, from_line=from_line)
        
        return jsonify({
            "success": True,
            "data": log_data
        })
        
    except Exception as e:
        logger.error(f"获取控制台日志失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500


@report_bp.route('/<report_id>/console-log/stream', methods=['GET'])
def stream_console_log(report_id: str):
    """
    获取完整的控制台日志（一次性获取全部）
    
    返回：
        {
            "success": true,
            "data": {
                "logs": [...],
                "count": 100
            }
        }
    """
    try:
        logs = ReportManager.get_console_log_stream(report_id)
        
        return jsonify({
            "success": True,
            "data": {
                "logs": logs,
                "count": len(logs)
            }
        })
        
    except Exception as e:
        logger.error(f"获取控制台日志失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500


# ============== 工具调用接口（供调试使用）==============

@report_bp.route('/tools/search', methods=['POST'])
def search_graph_tool():
    """
    图谱搜索工具接口（供调试使用）
    
    请求（JSON）：
        {
            "graph_id": "mirofish_xxxx",
            "query": "搜索查询",
            "limit": 10
        }
    """
    try:
        data = request.get_json() or {}
        
        graph_id = data.get('graph_id')
        query = data.get('query')
        limit = data.get('limit', 10)
        
        if not graph_id or not query:
            return jsonify({
                "success": False,
                "error": t('api.requireGraphIdAndQuery')
            }), 400
        
        from ..services.zep_tools import ZepToolsService
        
        tools = ZepToolsService()
        result = tools.search_graph(
            graph_id=graph_id,
            query=query,
            limit=limit
        )
        
        return jsonify({
            "success": True,
            "data": result.to_dict()
        })
        
    except Exception as e:
        logger.error(f"图谱搜索失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500


@report_bp.route('/tools/statistics', methods=['POST'])
def get_graph_statistics_tool():
    """
    图谱统计工具接口（供调试使用）
    
    请求（JSON）：
        {
            "graph_id": "mirofish_xxxx"
        }
    """
    try:
        data = request.get_json() or {}
        
        graph_id = data.get('graph_id')
        
        if not graph_id:
            return jsonify({
                "success": False,
                "error": t('api.requireGraphId')
            }), 400
        
        from ..services.zep_tools import ZepToolsService
        
        tools = ZepToolsService()
        result = tools.get_graph_statistics(graph_id)
        
        return jsonify({
            "success": True,
            "data": result
        })
        
    except Exception as e:
        logger.error(f"获取图谱统计失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500


# ============== Deep DD Interrogation endpoints ==============

@report_bp.route('/dd-interrogation', methods=['POST'])
def start_dd_interrogation():
    """
    Trigger Deep DD interrogation pass (async task)

    Request (JSON):
        {
            "simulation_id": "sim_xxxx",
            "graph_id": "mirofish_xxxx"
        }

    Returns:
        {
            "success": true,
            "data": {
                "simulation_id": "sim_xxxx",
                "task_id": "task_xxxx",
                "status": "running"
            }
        }
    """
    try:
        data = request.get_json() or {}

        simulation_id = data.get('simulation_id')
        graph_id = data.get('graph_id')

        if not simulation_id:
            return jsonify({
                "success": False,
                "error": t('api.requireSimulationId')
            }), 400

        if not graph_id:
            return jsonify({
                "success": False,
                "error": t('api.requireGraphId')
            }), 400

        manager = SimulationManager()
        state = manager.get_simulation(simulation_id)
        if not state:
            return jsonify({
                "success": False,
                "error": t('api.simulationNotFound', id=simulation_id)
            }), 404

        project = ProjectManager.get_project(state.project_id)
        simulation_requirement = project.simulation_requirement if project else ""

        task_manager = TaskManager()
        task_id = task_manager.create_task(
            task_type="dd_interrogation",
            metadata={
                "simulation_id": simulation_id,
                "graph_id": graph_id
            }
        )

        dd_progress_store[simulation_id] = {
            "status": "running",
            "current_question": 0,
            "current_domain": "INITIALISING",
            "found_count": 0,
            "partial_count": 0,
            "gap_count": 0,
            "potential_count": 0,
            "company_stage": "detecting...",
            "current_agent": "",
            "latest_log": "Deep DD interrogation initialising...",
            "answer_sheet": []
        }

        current_locale = get_locale()

        def run_dd():
            import time as _time
            set_locale(current_locale)
            try:
                task_manager.update_task(
                    task_id,
                    status=TaskStatus.PROCESSING,
                    progress=0,
                    message="Deep DD interrogation starting"
                )

                from ..services.zep_tools import ZepToolsService
                zep = ZepToolsService()

                DOMAINS = [
                    {
                        "name": "IDENTITY & STAGE",
                        "agent": "Lady Kaede",
                        "questions": [
                            {"text": "What specific milestone triggers the next funding round?", "stage_threshold": "all"},
                            {"text": "Is the one-line description defensible under scrutiny?", "stage_threshold": "all"},
                            {"text": "What is the current TRL and what evidence supports it?", "stage_threshold": "all"},
                            {"text": "Has the company defined its stage claim with precision?", "stage_threshold": "all"},
                            {"text": "What is the founding date and incorporation status?", "stage_threshold": "all"},
                            {"text": "Is there a clear pre-product or post-product distinction?", "stage_threshold": "all"},
                            {"text": "What is the team size and headcount breakdown?", "stage_threshold": "all"},
                            {"text": "Has the company achieved any revenue or paying customers?", "stage_threshold": "seed"},
                            {"text": "What is the current funding status and round history?", "stage_threshold": "all"},
                            {"text": "Is the product live or still in development?", "stage_threshold": "all"},
                            {"text": "What is the company legal entity and jurisdiction?", "stage_threshold": "all"},
                            {"text": "Has the company defined its use of funds clearly?", "stage_threshold": "all"},
                            {"text": "What IP does the company own or license?", "stage_threshold": "all"},
                            {"text": "Are PIIA agreements in place for all founders and staff?", "stage_threshold": "seed"},
                            {"text": "Has a cap table been disclosed with full UBO visibility?", "stage_threshold": "seed"},
                            {"text": "Are there any outstanding convertible instruments?", "stage_threshold": "seed"},
                            {"text": "What vesting schedule is in place for founders?", "stage_threshold": "seed"},
                            {"text": "Has the company defined a clear exit strategy?", "stage_threshold": "series_a"},
                            {"text": "What governance structure is in place?", "stage_threshold": "seed"},
                            {"text": "Is there a board of directors or advisors named?", "stage_threshold": "seed"},
                            {"text": "What is the company burn rate and runway?", "stage_threshold": "seed"},
                            {"text": "Has the company defined its go-to-market motion?", "stage_threshold": "all"},
                            {"text": "What is the customer acquisition cost at current stage?", "stage_threshold": "seed"},
                            {"text": "Is the seed document internally consistent on stage claims?", "stage_threshold": "all"}
                        ]
                    },
                    {
                        "name": "TECHNOLOGY & INNOVATION",
                        "agent": "Lord Reyoku",
                        "questions": [
                            {"text": "What is the hardest unsolved technical problem?", "stage_threshold": "all"},
                            {"text": "Does a clear technology development roadmap exist?", "stage_threshold": "all"},
                            {"text": "What has been demonstrated versus what is promised?", "stage_threshold": "all"},
                            {"text": "Is the core technology genuinely novel or recombinant?", "stage_threshold": "all"},
                            {"text": "What is the replication timeline for a well-funded competitor?", "stage_threshold": "all"},
                            {"text": "Has a third-party technical audit been conducted?", "stage_threshold": "seed"},
                            {"text": "What patents are filed granted or pending?", "stage_threshold": "seed"},
                            {"text": "What is the smart contract audit status if applicable?", "stage_threshold": "seed"},
                            {"text": "Is there a clear data strategy and data moat?", "stage_threshold": "all"},
                            {"text": "What open source dependencies create risk?", "stage_threshold": "seed"},
                            {"text": "Has the technology been tested in a production environment?", "stage_threshold": "seed"},
                            {"text": "What is the scalability ceiling of the current architecture?", "stage_threshold": "seed"},
                            {"text": "Is there a Zero to One test that this technology passes?", "stage_threshold": "all"},
                            {"text": "What technical debt exists in the current codebase?", "stage_threshold": "seed"},
                            {"text": "Has the company defined its build versus buy strategy?", "stage_threshold": "seed"},
                            {"text": "What cybersecurity posture has been documented?", "stage_threshold": "series_a"},
                            {"text": "Is there a disaster recovery and business continuity plan?", "stage_threshold": "series_a"},
                            {"text": "What is the technology dependency on third-party APIs?", "stage_threshold": "seed"},
                            {"text": "Has the company defined its data privacy architecture?", "stage_threshold": "series_a"},
                            {"text": "What monitoring and observability tooling is in place?", "stage_threshold": "series_a"},
                            {"text": "Is there a defined QA and testing framework?", "stage_threshold": "seed"},
                            {"text": "What is the current uptime and reliability record?", "stage_threshold": "series_a"}
                        ]
                    },
                    {
                        "name": "JURISDICTION & REGULATION",
                        "agent": "Shingen Iron Wolf",
                        "questions": [
                            {"text": "What is the regulatory classification in each target market?", "stage_threshold": "all"},
                            {"text": "Could the product be classified as a collective investment scheme?", "stage_threshold": "all"},
                            {"text": "Is the company subject to AML and KYC obligations?", "stage_threshold": "all"},
                            {"text": "Has a legal opinion been obtained on the regulatory status?", "stage_threshold": "seed"},
                            {"text": "What licences are required and which have been obtained?", "stage_threshold": "seed"},
                            {"text": "Is there an ongoing or threatened regulatory investigation?", "stage_threshold": "all"},
                            {"text": "How does the company handle cross-border data transfer?", "stage_threshold": "series_a"},
                            {"text": "What consumer protection obligations apply?", "stage_threshold": "seed"},
                            {"text": "Has the company engaged with regulators proactively?", "stage_threshold": "seed"},
                            {"text": "What is the VASP classification status if applicable?", "stage_threshold": "all"},
                            {"text": "Is the company subject to Basel III or equivalent constraints?", "stage_threshold": "series_a"},
                            {"text": "What sanctions screening is in place?", "stage_threshold": "seed"},
                            {"text": "Has the company defined its regulatory change management process?", "stage_threshold": "series_a"},
                            {"text": "What is the liability exposure in each jurisdiction?", "stage_threshold": "seed"},
                            {"text": "Are terms of service and privacy policy legally reviewed?", "stage_threshold": "seed"},
                            {"text": "Has the company obtained any regulatory sandbox approval?", "stage_threshold": "seed"},
                            {"text": "What is the dispute resolution framework?", "stage_threshold": "series_a"},
                            {"text": "Is there a dedicated compliance officer or team?", "stage_threshold": "series_a"}
                        ]
                    },
                    {
                        "name": "CAPITAL & BUSINESS MODEL",
                        "agent": "Lord Renji",
                        "questions": [
                            {"text": "What happens if the primary revenue assumption is wrong by 50%?", "stage_threshold": "all"},
                            {"text": "Are unit economics at scale documented and credible?", "stage_threshold": "seed"},
                            {"text": "What is the current ARR or MRR?", "stage_threshold": "seed"},
                            {"text": "What is the contribution margin per customer?", "stage_threshold": "series_a"},
                            {"text": "Can the business model survive without continuous external capital?", "stage_threshold": "all"},
                            {"text": "What are the top three cost drivers?", "stage_threshold": "all"},
                            {"text": "Is there a clear path to profitability without heroic assumptions?", "stage_threshold": "all"},
                            {"text": "What is the LTV to CAC ratio at current and projected scale?", "stage_threshold": "series_a"},
                            {"text": "Has the company stress-tested the model against regulatory shifts?", "stage_threshold": "seed"},
                            {"text": "What revenue streams are direct versus indirect?", "stage_threshold": "all"},
                            {"text": "Is pricing strategy documented and validated with customers?", "stage_threshold": "seed"},
                            {"text": "What is the gross margin profile at target scale?", "stage_threshold": "seed"},
                            {"text": "Has the company defined its Rule of 40 trajectory?", "stage_threshold": "series_a"},
                            {"text": "What working capital requirements exist at scale?", "stage_threshold": "series_a"},
                            {"text": "Is there a clear fundraising plan with milestone alignment?", "stage_threshold": "all"},
                            {"text": "What is the EBITDA trend over the last 12 months?", "stage_threshold": "series_b"},
                            {"text": "Has the company defined its capital efficiency metrics?", "stage_threshold": "series_a"},
                            {"text": "What debt obligations exist or are planned?", "stage_threshold": "seed"},
                            {"text": "Is the funding ask proportionate to the milestones?", "stage_threshold": "all"},
                            {"text": "What is the financial model sensitivity to churn?", "stage_threshold": "series_a"},
                            {"text": "Has the company modelled a downside scenario?", "stage_threshold": "seed"},
                            {"text": "What is the payback period per customer acquired?", "stage_threshold": "series_a"},
                            {"text": "Is there a treasury management policy in place?", "stage_threshold": "series_a"},
                            {"text": "What is the burn multiple at current revenue?", "stage_threshold": "seed"},
                            {"text": "Has the company defined its investor return scenario?", "stage_threshold": "seed"},
                            {"text": "What is the net revenue retention rate?", "stage_threshold": "series_a"},
                            {"text": "Is there a defined dividend or distribution policy?", "stage_threshold": "series_b"},
                            {"text": "What is the break-even timeline under base case?", "stage_threshold": "all"}
                        ]
                    },
                    {
                        "name": "MARKET & COMPETITION",
                        "agent": "Lady Asami",
                        "questions": [
                            {"text": "Who are the direct competitors and what is their funding status?", "stage_threshold": "all"},
                            {"text": "Who are the indirect competitors that could enter this space?", "stage_threshold": "all"},
                            {"text": "Is the market sizing methodology bottom-up or top-down?", "stage_threshold": "all"},
                            {"text": "What assumptions underpin the TAM SAM and SOM figures?", "stage_threshold": "all"},
                            {"text": "What is the competitive response time if this company succeeds?", "stage_threshold": "all"},
                            {"text": "Has the company validated market size with primary research?", "stage_threshold": "all"},
                            {"text": "What switching costs exist for customers choosing this product?", "stage_threshold": "seed"},
                            {"text": "Is there evidence of product-market fit from early adopters?", "stage_threshold": "seed"},
                            {"text": "What is the customer concentration risk?", "stage_threshold": "series_a"},
                            {"text": "Has the company defined its market entry sequencing?", "stage_threshold": "all"},
                            {"text": "What barriers to entry does the company create over time?", "stage_threshold": "all"},
                            {"text": "Is there a documented competitive intelligence process?", "stage_threshold": "series_a"},
                            {"text": "What is the net promoter score or equivalent satisfaction metric?", "stage_threshold": "series_a"},
                            {"text": "Has the company identified its beachhead market precisely?", "stage_threshold": "all"},
                            {"text": "What is the market growth rate and what drives it?", "stage_threshold": "all"},
                            {"text": "Are there network effects that compound the competitive moat?", "stage_threshold": "all"},
                            {"text": "What is the sales cycle length and what drives it?", "stage_threshold": "seed"},
                            {"text": "Has the company mapped the full customer journey?", "stage_threshold": "seed"},
                            {"text": "What channel partnerships are in place or planned?", "stage_threshold": "seed"},
                            {"text": "Is there a documented land and expand strategy?", "stage_threshold": "series_a"},
                            {"text": "What is the average contract value and how does it trend?", "stage_threshold": "series_a"},
                            {"text": "Has the company defined its ideal customer profile precisely?", "stage_threshold": "all"},
                            {"text": "What is the churn rate and what are the primary churn drivers?", "stage_threshold": "series_a"},
                            {"text": "Is there a documented win-loss analysis from sales?", "stage_threshold": "series_a"},
                            {"text": "What is the pipeline coverage ratio?", "stage_threshold": "series_a"},
                            {"text": "Has the company defined its category creation or entry strategy?", "stage_threshold": "all"},
                            {"text": "What is the quota attainment rate of the sales team?", "stage_threshold": "series_b"},
                            {"text": "What is the time to first value for a new customer?", "stage_threshold": "series_a"},
                            {"text": "Has the company identified regulatory tailwinds or headwinds?", "stage_threshold": "all"},
                            {"text": "Is there a documented referral or word-of-mouth growth loop?", "stage_threshold": "seed"},
                            {"text": "What is the market concentration fragmented or consolidated?", "stage_threshold": "all"},
                            {"text": "Has the company defined its pricing power over time?", "stage_threshold": "seed"}
                        ]
                    },
                    {
                        "name": "TEAM & CREDIBILITY",
                        "agent": "Lady Kaede",
                        "questions": [
                            {"text": "Has the full founding team worked together before?", "stage_threshold": "all"},
                            {"text": "What is the single biggest team gap and the plan to fill it?", "stage_threshold": "all"},
                            {"text": "Do the founders have relevant domain expertise for this sector?", "stage_threshold": "all"},
                            {"text": "Have any co-founders departed and under what circumstances?", "stage_threshold": "all"},
                            {"text": "What is the equity split and is it defensible?", "stage_threshold": "all"},
                            {"text": "Is there evidence of founder-market fit beyond biography?", "stage_threshold": "all"},
                            {"text": "What is the combined execution history of the team?", "stage_threshold": "all"},
                            {"text": "Are there any conflicts of interest among team members?", "stage_threshold": "all"},
                            {"text": "What advisors are named and what is their actual involvement?", "stage_threshold": "all"},
                            {"text": "Has the team demonstrated ability to hire and retain talent?", "stage_threshold": "seed"},
                            {"text": "What is the leadership style and decision-making framework?", "stage_threshold": "seed"},
                            {"text": "Are there any legal disputes involving founders personally?", "stage_threshold": "all"},
                            {"text": "What is the team track record on previous commitments?", "stage_threshold": "all"},
                            {"text": "Has the company defined its culture and values explicitly?", "stage_threshold": "series_a"},
                            {"text": "Is there a succession plan for key person dependency?", "stage_threshold": "series_a"},
                            {"text": "What is the team network strength in the target sector?", "stage_threshold": "all"},
                            {"text": "Has the company defined its hiring plan for the next 18 months?", "stage_threshold": "seed"},
                            {"text": "Are compensation packages market-competitive?", "stage_threshold": "series_a"},
                            {"text": "Is there a defined performance management framework?", "stage_threshold": "series_a"},
                            {"text": "Has the team demonstrated coachability under pressure?", "stage_threshold": "all"},
                            {"text": "What references are available for the founding team?", "stage_threshold": "all"},
                            {"text": "Is there a documented onboarding process for new hires?", "stage_threshold": "series_a"},
                            {"text": "What is the current employee NPS?", "stage_threshold": "series_b"},
                            {"text": "Has the company defined its remote or office working policy?", "stage_threshold": "series_a"}
                        ]
                    }
                ]

                answer_sheet = []
                q_current = 0
                found_count = 0
                partial_count = 0
                gap_count = 0
                potential_count = 0

                # ── Stage detection ──────────────────────────────────
                dd_progress_store[simulation_id]["latest_log"] = (
                    "Detecting company stage from simulation graph..."
                )
                try:
                    stage_result = zep.quick_search(
                        graph_id=graph_id,
                        query="company stage funding round TRL seed pre-seed series MVP",
                        limit=10
                    )
                    stage_text = " ".join(
                        stage_result.facts if stage_result.facts else []
                    ).lower()
                except Exception:
                    stage_text = ""

                if any(x in stage_text for x in [
                    "pre-seed", "pre seed", "accelerator",
                    "crowdfunding", "idea stage", "trl 1", "trl 2", "trl 3"
                ]):
                    company_stage = "pre_seed"
                elif any(x in stage_text for x in [
                    "seed", "trl 4", "trl 5", "mvp", "prototype"
                ]):
                    company_stage = "seed"
                elif any(x in stage_text for x in [
                    "series a", "series-a", "trl 6", "trl 7"
                ]):
                    company_stage = "series_a"
                elif any(x in stage_text for x in [
                    "series b", "series-b", "series c", "trl 8", "trl 9"
                ]):
                    company_stage = "series_b"
                else:
                    company_stage = "seed"

                dd_progress_store[simulation_id]["latest_log"] = (
                    f"Company stage detected: {company_stage.upper()} — "
                    f"fetching full simulation graph..."
                )

                # ── Single panorama fetch ─────────────────────────────
                try:
                    panorama = zep.panorama_search(
                        graph_id=graph_id,
                        query=simulation_requirement,
                        include_expired=False
                    )
                    all_facts = panorama.active_facts or []
                except Exception as pe:
                    logger.warning(f"Panorama fetch failed: {pe}")
                    all_facts = []

                dd_progress_store[simulation_id]["latest_log"] = (
                    f"Graph loaded — {len(all_facts)} facts indexed. "
                    f"Beginning interrogation..."
                )

                # ── Keyword extractor ─────────────────────────────────
                STOP_WORDS = {
                    "what","is","the","are","has","have","does","do",
                    "been","a","an","in","of","for","to","and","or",
                    "its","their","any","this","that","with","from",
                    "how","who","which","where","when","will","can",
                    "could","should","would","there","be","if","not",
                    "it","at","on","by","as","all","each","per","only",
                    "also","both","more","most","least","fully","clearly",
                    "currently","specifically","whether","company","companies",
                    "investor","investors","investment","founder","founders",
                    "market","markets","business","model","stage","current",
                    "plan","plans","strategy","strategic","rate","rates",
                    "defined","define","documented","document","evidence",
                    "demonstrated","demonstrate","identify","identified",
                    "established","establish","ensure","ensuring","clear",
                    "specific","explicitly","implicit","noted","note",
                    "indicate","indicates","indicate","relevant","required",
                    "require","exist","existing","exists","place","based",
                    "provide","provides","provided","including","included",
                    "across","within","between","against","toward","around",
                    "potential","capital","team","product","customer","customers",
                    "growth","revenue","funding","raise","raised","round",
                    "series","seed","early","late","next","first","last",
                    "year","years","month","months","quarter","quarters",
                    "number","numbers","amount","amounts","level","levels",
                    "high","low","strong","weak","good","bad","better","best"
                }

                def extract_keywords(text):
                    words = text.lower().replace("?","").replace(",","").split()
                    return [w for w in words if w not in STOP_WORDS and len(w) > 3]

                def score_question(question, facts):
                    keywords = extract_keywords(question)
                    if not keywords:
                        return [], 0

                    # Build two-word phrases from the question
                    # for stronger matching
                    words = question.lower().replace("?","").split()
                    meaningful = [w for w in words if w not in STOP_WORDS and len(w) > 3]
                    phrases = []
                    for i in range(len(meaningful) - 1):
                        phrases.append(f"{meaningful[i]} {meaningful[i+1]}")

                    hits = []
                    for fact in facts:
                        fact_lower = fact.lower()

                        # Phrase match — strongest signal
                        phrase_hits = sum(
                            1 for ph in phrases if ph in fact_lower
                        )
                        if phrase_hits >= 1:
                            hits.append(fact)
                            continue

                        # Keyword match — require more matches
                        # for shorter keyword lists
                        kw_matches = sum(
                            1 for kw in keywords if kw in fact_lower
                        )
                        min_required = max(3, len(keywords) // 2)
                        if kw_matches >= min_required:
                            hits.append(fact)

                    return hits, len(hits)

                # ── Stage threshold checker ───────────────────────────
                STAGE_ORDER = {
                    "all": 0,
                    "pre_seed": 1,
                    "seed": 2,
                    "series_a": 3,
                    "series_b": 4
                }

                def is_stage_appropriate(threshold):
                    return (
                        STAGE_ORDER.get(company_stage, 2) >=
                        STAGE_ORDER.get(threshold, 0)
                    )

                # ── Potential framing generator ───────────────────────
                from ..utils.llm_client import LLMClient
                _llm = LLMClient()

                def generate_potential_framing(question, domain_name, facts):
                    context = "\n".join(facts[:5]) if facts else "No direct evidence found."
                    company_hint = simulation_requirement.split('\n')[0][:120]
                    try:
                        prompt = (
                            f"You are a senior investment analyst reviewing a "
                            f"{company_stage.replace('_',' ')} stage company.\n\n"
                            f"Company context: {company_hint}\n\n"
                            f"Simulation evidence available:\n{context}\n\n"
                            f"Due diligence question (not yet applicable at this "
                            f"stage): {question}\n\n"
                            f"Write ONE concise sentence (max 40 words) in this "
                            f"format: 'If [company] achieves [specific milestone "
                            f"from evidence], then [this metric/question] becomes "
                            f"[specific investor signal].' "
                            f"Be specific to this company. Do not be generic."
                        )
                        response = _llm.chat(
                            messages=[{"role": "user", "content": prompt}],
                            temperature=0.3,
                            max_tokens=80
                        )
                        return response.strip() if response else ""
                    except Exception:
                        return (
                            f"At {company_stage.replace('_',' ')} stage this "
                            f"metric is not yet applicable — address at next "
                            f"funding milestone."
                        )

                # ── Main interrogation loop ───────────────────────────
                for domain in DOMAINS:
                    dd_progress_store[simulation_id]["current_domain"] = (
                        domain["name"]
                    )
                    dd_progress_store[simulation_id]["current_agent"] = (
                        domain["agent"]
                    )
                    dd_progress_store[simulation_id]["latest_log"] = (
                        f"Domain: {domain['name']} — "
                        f"{domain['agent']} activated"
                    )

                    for q_item in domain["questions"]:
                        question = q_item["text"]
                        threshold = q_item.get("stage_threshold", "all")

                        try:
                            hits, hit_count = score_question(
                                question, all_facts
                            )

                            if not is_stage_appropriate(threshold):
                                framing = generate_potential_framing(
                                    question, domain["name"], hits
                                )
                                status = "potential"
                                potential_count += 1
                                answer_sheet.append({
                                    "domain": domain["name"],
                                    "agent": domain["agent"],
                                    "question": question,
                                    "stage_threshold": threshold,
                                    "company_stage": company_stage,
                                    "status": "potential",
                                    "stage_note": (
                                        f"{company_stage.replace('_',' ').title()} "
                                        f"stage — this question is not yet applicable"
                                    ),
                                    "potential_framing": framing,
                                    "evidence": hits[:3],
                                    "evidence_count": hit_count
                                })
                            elif hit_count >= 2:
                                status = "found"
                                found_count += 1
                                answer_sheet.append({
                                    "domain": domain["name"],
                                    "agent": domain["agent"],
                                    "question": question,
                                    "stage_threshold": threshold,
                                    "company_stage": company_stage,
                                    "status": "found",
                                    "evidence": hits[:3],
                                    "evidence_count": hit_count
                                })
                            elif hit_count == 1:
                                status = "partial"
                                partial_count += 1
                                answer_sheet.append({
                                    "domain": domain["name"],
                                    "agent": domain["agent"],
                                    "question": question,
                                    "stage_threshold": threshold,
                                    "company_stage": company_stage,
                                    "status": "partial",
                                    "evidence": hits[:3],
                                    "evidence_count": hit_count
                                })
                            else:
                                status = "gap"
                                gap_count += 1
                                answer_sheet.append({
                                    "domain": domain["name"],
                                    "agent": domain["agent"],
                                    "question": question,
                                    "stage_threshold": threshold,
                                    "company_stage": company_stage,
                                    "status": "gap",
                                    "evidence": [],
                                    "evidence_count": 0
                                })

                            q_current += 1
                            dd_progress_store[simulation_id].update({
                    "status": "complete",
                    "current_question": q_current,
                    "found_count": found_count,
                    "partial_count": partial_count,
                    "gap_count": gap_count,
                    "potential_count": potential_count,
                    "company_stage": company_stage,
                    "latest_log": "DD interrogation complete — answer sheet compiled",
                    "answer_sheet": answer_sheet
                })

                            task_manager.update_task(
                                task_id,
                                progress=int((q_current / 148) * 100),
                                message=(
                                    f"DD Q{q_current}/148 — "
                                    f"{domain['name']}"
                                )
                            )

                        except Exception as qe:
                            logger.warning(
                                f"DD question failed: {str(qe)}"
                            )
                            answer_sheet.append({
                                "domain": domain["name"],
                                "agent": domain["agent"],
                                "question": question,
                                "status": "gap",
                                "evidence": [],
                                "evidence_count": 0
                            })
                            q_current += 1
                            gap_count += 1

                

                dd_progress_store[simulation_id].update({
                    "status": "complete",
                    "current_question": q_current,
                    "found_count": found_count,
                    "partial_count": partial_count,
                    "gap_count": gap_count,
                    "latest_log": "DD interrogation complete — answer sheet compiled",
                    "answer_sheet": answer_sheet
                })

                _save_dd_answer_sheet(simulation_id, answer_sheet)

                task_manager.complete_task(
                    task_id,
                    result={
                        "simulation_id": simulation_id,
                        "total_questions": q_current,
                        "found": found_count,
                        "partial": partial_count,
                        "gaps": gap_count,
                        "potential": potential_count,
                        "company_stage": company_stage,
                        "status": "complete"
                    }
                )

            except Exception as e:
                logger.error(f"DD interrogation failed: {str(e)}")
                dd_progress_store[simulation_id]["status"] = "failed"
                dd_progress_store[simulation_id]["latest_log"] = f"Error: {str(e)}"
                task_manager.fail_task(task_id, str(e))

        thread = threading.Thread(target=run_dd, daemon=True)
        thread.start()

        return jsonify({
            "success": True,
            "data": {
                "simulation_id": simulation_id,
                "task_id": task_id,
                "status": "running",
                "message": "Deep DD interrogation started"
            }
        })

    except Exception as e:
        logger.error(f"Failed to start DD interrogation: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500


@report_bp.route('/dd-progress', methods=['GET'])
def get_dd_progress():
    """
    Get live Deep DD interrogation progress

    Query params:
        simulation_id: simulation ID

    Returns:
        {
            "success": true,
            "data": {
                "status": "running|complete|failed",
                "current_question": 42,
                "current_domain": "CAPITAL & BUSINESS MODEL",
                "found_count": 28,
                "partial_count": 9,
                "gap_count": 5,
                "current_agent": "Lord Renji",
                "latest_log": "Q42: Unit economics..."
            }
        }
    """
    try:
        simulation_id = request.args.get('simulation_id')
        if not simulation_id:
            return jsonify({
                "success": False,
                "error": t('api.requireSimulationId')
            }), 400

        progress = dd_progress_store.get(simulation_id)
        if not progress:
            return jsonify({
                "success": False,
                "error": "No DD interrogation found for this simulation"
            }), 404

        safe_progress = {k: v for k, v in progress.items() if k != "answer_sheet"}

        return jsonify({
            "success": True,
            "data": safe_progress
        })

    except Exception as e:
        logger.error(f"Failed to get DD progress: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@report_bp.route('/dd-answer-sheet', methods=['GET'])
def get_dd_answer_sheet():
    """
    Download the DD answer sheet JSON for a simulation
    Query params:
        simulation_id: simulation ID
    Returns JSON file download
    """
    try:
        simulation_id = request.args.get('simulation_id')
        if not simulation_id:
            return jsonify({
                "success": False,
                "error": t('api.requireSimulationId')
            }), 400

        sheet_path = _get_dd_answer_sheet_path(simulation_id)

        if not os.path.exists(sheet_path):
            progress = dd_progress_store.get(simulation_id, {})
            answer_sheet = progress.get("answer_sheet", [])
            if not answer_sheet:
                return jsonify({
                    "success": False,
                    "error": "DD answer sheet not found for this simulation"
                }), 404
            import tempfile, json as _json
            with tempfile.NamedTemporaryFile(
                mode='w', suffix='.json', delete=False, encoding='utf-8'
            ) as f:
                _json.dump(answer_sheet, f, ensure_ascii=False, indent=2)
                sheet_path = f.name

        return send_file(
            sheet_path,
            as_attachment=True,
            download_name=f"dd_answer_sheet_{simulation_id}.json",
            mimetype='application/json'
        )

    except Exception as e:
        logger.error(f"Failed to get DD answer sheet: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


def _get_dd_answer_sheet_path(simulation_id: str) -> str:
    """Get the file path for a DD answer sheet"""
    return os.path.join(
        Config.UPLOAD_FOLDER, 'dd_sheets',
        f"dd_{simulation_id}.json"
    )


def _save_dd_answer_sheet(simulation_id: str, answer_sheet: list) -> None:
    """Save DD answer sheet to disk"""
    import json as _json
    sheet_dir = os.path.join(Config.UPLOAD_FOLDER, 'dd_sheets')
    os.makedirs(sheet_dir, exist_ok=True)
    path = _get_dd_answer_sheet_path(simulation_id)
    with open(path, 'w', encoding='utf-8') as f:
        _json.dump(answer_sheet, f, ensure_ascii=False, indent=2)
    logger.info(f"DD answer sheet saved: {path}")
            
