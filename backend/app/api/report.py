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
                    status=TaskStatus.PROCESSING,
                    progress=0,
                    message=t('api.initReportAgent')
                )
                
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
            "current_agent": "",
            "latest_log": "Deep DD interrogation initialising...",
            "answer_sheet": []
        }

        current_locale = get_locale()

        def run_dd():
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
                            "What specific milestone triggers the next funding round?",
                            "Is the one-line description defensible under scrutiny?",
                            "What is the current TRL and what evidence supports it?",
                            "Has the company defined its stage claim with precision?",
                            "What is the founding date and incorporation status?",
                            "Is there a clear pre-product or post-product distinction?",
                            "What is the team size and headcount breakdown?",
                            "Has the company achieved any revenue or paying customers?",
                            "What is the current funding status and round history?",
                            "Is the product live or still in development?",
                            "What is the company's legal entity and jurisdiction?",
                            "Has the company defined its use of funds clearly?",
                            "What IP does the company own or license?",
                            "Are PIIA agreements in place for all founders and staff?",
                            "Has a cap table been disclosed with full UBO visibility?",
                            "Are there any outstanding convertible instruments?",
                            "What vesting schedule is in place for founders?",
                            "Has the company defined a clear exit strategy?",
                            "What governance structure is in place?",
                            "Is there a board of directors or advisors named?",
                            "What is the company's burn rate and runway?",
                            "Has the company defined its go-to-market motion?",
                            "What is the customer acquisition cost at current stage?",
                            "Is the seed document internally consistent on stage claims?"
                        ]
                    },
                    {
                        "name": "TECHNOLOGY & INNOVATION",
                        "agent": "Lord Reyoku",
                        "questions": [
                            "What is the hardest unsolved technical problem?",
                            "Does a clear technology development roadmap exist?",
                            "What has been demonstrated versus what is promised?",
                            "Is the core technology genuinely novel or recombinant?",
                            "What is the replication timeline for a well-funded competitor?",
                            "Has a third-party technical audit been conducted?",
                            "What patents are filed, granted, or pending?",
                            "What is the smart contract audit status if applicable?",
                            "Is there a clear data strategy and data moat?",
                            "What open source dependencies create risk?",
                            "Has the technology been tested in a production environment?",
                            "What is the scalability ceiling of the current architecture?",
                            "Is there a Zero to One test that this technology passes?",
                            "What technical debt exists in the current codebase?",
                            "Has the company defined its build versus buy strategy?",
                            "What cybersecurity posture has been documented?",
                            "Is there a disaster recovery and business continuity plan?",
                            "What is the technology's dependency on third-party APIs?",
                            "Has the company defined its data privacy architecture?",
                            "What monitoring and observability tooling is in place?",
                            "Is there a defined QA and testing framework?",
                            "What is the current uptime and reliability record?"
                        ]
                    },
                    {
                        "name": "JURISDICTION & REGULATION",
                        "agent": "Shingen Iron Wolf",
                        "questions": [
                            "What is the regulatory classification in each target market?",
                            "Could the product be classified as a collective investment scheme?",
                            "Is the company subject to AML and KYC obligations?",
                            "Has a legal opinion been obtained on the regulatory status?",
                            "What licences are required and which have been obtained?",
                            "Is there an ongoing or threatened regulatory investigation?",
                            "How does the company handle cross-border data transfer?",
                            "What consumer protection obligations apply?",
                            "Has the company engaged with regulators proactively?",
                            "What is the VASP classification status if applicable?",
                            "Is the company subject to Basel III or equivalent constraints?",
                            "What sanctions screening is in place?",
                            "Has the company defined its regulatory change management process?",
                            "What is the liability exposure in each jurisdiction?",
                            "Are terms of service and privacy policy legally reviewed?",
                            "Has the company obtained any regulatory sandbox approval?",
                            "What is the dispute resolution framework?",
                            "Is there a dedicated compliance officer or team?"
                        ]
                    },
                    {
                        "name": "CAPITAL & BUSINESS MODEL",
                        "agent": "Lord Renji",
                        "questions": [
                            "What happens if the primary revenue assumption is wrong by 50%?",
                            "Are unit economics at scale documented and credible?",
                            "What is the current ARR or MRR?",
                            "What is the contribution margin per customer?",
                            "Can the business model survive without continuous external capital?",
                            "What are the top three cost drivers?",
                            "Is there a clear path to profitability without heroic assumptions?",
                            "What is the LTV to CAC ratio at current and projected scale?",
                            "Has the company stress-tested the model against regulatory shifts?",
                            "What revenue streams are direct versus indirect?",
                            "Is pricing strategy documented and validated with customers?",
                            "What is the gross margin profile at target scale?",
                            "Has the company defined its Rule of 40 trajectory?",
                            "What working capital requirements exist at scale?",
                            "Is there a clear fundraising plan with milestone alignment?",
                            "What is the EBITDA trend over the last 12 months?",
                            "Has the company defined its capital efficiency metrics?",
                            "What debt obligations exist or are planned?",
                            "Is the funding ask proportionate to the milestones?",
                            "What is the financial model's sensitivity to churn?",
                            "Has the company modelled a downside scenario?",
                            "What is the payback period per customer acquired?",
                            "Is there a treasury management policy in place?",
                            "What is the burn multiple at current revenue?",
                            "Has the company defined its investor return scenario?",
                            "What is the net revenue retention rate?",
                            "Is there a defined dividend or distribution policy?",
                            "What is the break-even timeline under base case?"
                        ]
                    },
                    {
                        "name": "MARKET & COMPETITION",
                        "agent": "Lady Asami",
                        "questions": [
                            "Who are the direct competitors and what is their funding status?",
                            "Who are the indirect competitors that could enter this space?",
                            "Is the market sizing methodology bottom-up or top-down?",
                            "What assumptions underpin the TAM, SAM, and SOM figures?",
                            "What is the competitive response time if this company succeeds?",
                            "Has the company validated market size with primary research?",
                            "What switching costs exist for customers choosing this product?",
                            "Is there evidence of product-market fit from early adopters?",
                            "What is the customer concentration risk?",
                            "Has the company defined its market entry sequencing?",
                            "What barriers to entry does the company create over time?",
                            "Is there a documented competitive intelligence process?",
                            "What is the net promoter score or equivalent satisfaction metric?",
                            "Has the company identified its beachhead market precisely?",
                            "What is the market growth rate and what drives it?",
                            "Are there network effects that compound the competitive moat?",
                            "What is the sales cycle length and what drives it?",
                            "Has the company mapped the full customer journey?",
                            "What channel partnerships are in place or planned?",
                            "Is there a documented land and expand strategy?",
                            "What is the average contract value and how does it trend?",
                            "Has the company defined its ideal customer profile precisely?",
                            "What is the churn rate and what are the primary churn drivers?",
                            "Is there a documented win-loss analysis from sales?",
                            "What is the pipeline coverage ratio?",
                            "Has the company defined its category creation or category entry strategy?",
                            "What is the quota attainment rate of the sales team?",
                            "What is the time to first value for a new customer?",
                            "Has the company identified regulatory tailwinds or headwinds?",
                            "Is there a documented referral or word-of-mouth growth loop?",
                            "What is the market concentration — fragmented or consolidated?",
                            "Has the company defined its pricing power over time?"
                        ]
                    },
                    {
                        "name": "TEAM & CREDIBILITY",
                        "agent": "Lady Kaede",
                        "questions": [
                            "Has the full founding team worked together before?",
                            "What is the single biggest team gap and the plan to fill it?",
                            "Do the founders have relevant domain expertise for this sector?",
                            "Have any co-founders departed and under what circumstances?",
                            "What is the equity split and is it defensible?",
                            "Is there evidence of founder-market fit beyond biography?",
                            "What is the combined execution history of the team?",
                            "Are there any conflicts of interest among team members?",
                            "What advisors are named and what is their actual involvement?",
                            "Has the team demonstrated ability to hire and retain talent?",
                            "What is the leadership style and decision-making framework?",
                            "Are there any legal disputes involving founders personally?",
                            "What is the team's track record on previous commitments?",
                            "Has the company defined its culture and values explicitly?",
                            "Is there a succession plan for key person dependency?",
                            "What is the team's network strength in the target sector?",
                            "Has the company defined its hiring plan for the next 18 months?",
                            "Are compensation packages market-competitive?",
                            "Is there a defined performance management framework?",
                            "Has the team demonstrated coachability under pressure?",
                            "What references are available for the founding team?",
                            "Is there a documented onboarding process for new hires?",
                            "What is the current employee NPS?",
                            "Has the company defined its remote or office working policy?"
                        ]
                    }
                ]

                answer_sheet = []
                q_current = 0
                found_count = 0
                partial_count = 0
                gap_count = 0

                for domain in DOMAINS:
                    dd_progress_store[simulation_id]["current_domain"] = domain["name"]
                    dd_progress_store[simulation_id]["current_agent"] = domain["agent"]
                    dd_progress_store[simulation_id]["latest_log"] = (
                        f"Domain: {domain['name']} — {domain['agent']} activated"
                    )

                    for question in domain["questions"]:
                        try:
                            company_hint = simulation_requirement.split('\n')[0][:80]
enriched_query = f"{company_hint} — {question}"
result = zep.quick_search(
    graph_id=graph_id,
    query=enriched_query,
    limit=5
)

                            facts = result.facts if result.facts else []
                            fact_count = len(facts)

                            if fact_count >= 3:
                                status = "found"
                                found_count += 1
                            elif fact_count >= 1:
                                status = "partial"
                                partial_count += 1
                            else:
                                status = "gap"
                                gap_count += 1

                            answer_sheet.append({
                                "domain": domain["name"],
                                "agent": domain["agent"],
                                "question": question,
                                "status": status,
                                "evidence": facts[:3],
                                "evidence_count": fact_count
                            })

                            q_current += 1
                            dd_progress_store[simulation_id].update({
                                "current_question": q_current,
                                "found_count": found_count,
                                "partial_count": partial_count,
                                "gap_count": gap_count,
                                "latest_log": (
                                    f"Q{q_current}: {question[:60]}... "
                                    f"[{status.upper()}]"
                                )
                            })

                            task_manager.update_task(
                                task_id,
                                progress=int((q_current / 148) * 100),
                                message=f"DD Q{q_current}/148 — {domain['name']}"
                            )

                        except Exception as qe:
                            logger.warning(f"DD question failed: {str(qe)}")
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
            
