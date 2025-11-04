"""
Web 路由定义
"""
import os
import pandas as pd
import pickle
import logging
from flask import (
    render_template, request, jsonify, session,
    redirect, url_for, send_file
)
from werkzeug.exceptions import RequestEntityTooLarge

from core import file_handler, validator, comparison, exporter

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def register_routes(app):
    """注册所有路由到 Flask 应用"""

    # 在应用启动时初始化模板校验器
    validator.init_validator(app.config['TEMPLATES_FOLDER'])

    @app.route('/')
    def index():
        """主页面 - 文件上传表单"""
        # 为新用户创建会话 ID
        if 'session_id' not in session:
            session['session_id'] = file_handler.get_session_id()
            logger.info(f"创建新会话: {session['session_id']}")

        return render_template('index.html')

    @app.route('/upload/local', methods=['POST'])
    def upload_local():
        """处理单机库文件上传和校验"""
        try:
            # 检查文件是否存在
            if 'file' not in request.files:
                return jsonify({
                    'success': False,
                    'error': '未提供文件'
                }), 400

            file = request.files['file']

            if file.filename == '':
                return jsonify({
                    'success': False,
                    'error': '未选择文件'
                }), 400

            # 获取或创建会话目录
            session_id = session.get('session_id')
            if not session_id:
                session_id = file_handler.get_session_id()
                session['session_id'] = session_id

            session_dir = file_handler.create_session_directory(
                app.config['UPLOAD_FOLDER'],
                session_id
            )

            # 保存文件
            filepath = file_handler.save_uploaded_file(file, session_dir, 'local.xls')

            # 校验模板
            val = validator.get_validator()
            validation_result = val.validate_local_template(filepath)

            if validation_result['valid']:
                session['local_file'] = filepath
                return jsonify({
                    'success': True,
                    'valid': True,
                    'message': '文件上传成功，格式校验通过'
                })
            else:
                # 校验失败，删除文件并清除session
                if os.path.exists(filepath):
                    os.remove(filepath)
                session.pop('local_file', None)  # 清除session中的文件路径
                error_msg = '上传表格格式不正确'

                # 添加详细的列位置信息
                if validation_result.get('column_details'):
                    details = validation_result['column_details']
                    error_msg += '：'
                    detail_msgs = []
                    for detail in details[:5]:  # 最多显示前5个差异
                        detail_msgs.append(
                            f"{detail['position']}应为'{detail['expected']}'，实际为'{detail['actual']}'"
                        )
                    error_msg += '；'.join(detail_msgs)
                    if len(details) > 5:
                        error_msg += f'；等共{len(details)}处差异'
                elif validation_result.get('order_mismatch'):
                    error_msg += "，列顺序不匹配"
                elif 'missing_columns' in validation_result and validation_result['missing_columns']:
                    error_msg += f"，缺少列: {', '.join(validation_result['missing_columns'])}"

                if 'error' in validation_result:
                    error_msg = validation_result['error']

                return jsonify({
                    'success': True,
                    'valid': False,
                    'error': error_msg,
                    'column_details': validation_result.get('column_details', [])
                })

        except ValueError as e:
            session.pop('local_file', None)  # 清除session
            return jsonify({'success': False, 'error': str(e)}), 400
        except Exception as e:
            session.pop('local_file', None)  # 清除session
            logger.error(f"上传单机库文件失败: {e}")
            return jsonify({'success': False, 'error': '文件上传失败'}), 500

    @app.route('/upload/national', methods=['POST'])
    def upload_national():
        """处理全国库文件上传和校验"""
        try:
            if 'file' not in request.files:
                return jsonify({
                    'success': False,
                    'error': '未提供文件'
                }), 400

            file = request.files['file']

            if file.filename == '':
                return jsonify({
                    'success': False,
                    'error': '未选择文件'
                }), 400

            # 获取或创建会话目录
            session_id = session.get('session_id')
            if not session_id:
                session_id = file_handler.get_session_id()
                session['session_id'] = session_id

            session_dir = file_handler.create_session_directory(
                app.config['UPLOAD_FOLDER'],
                session_id
            )

            # 保存文件
            filepath = file_handler.save_uploaded_file(file, session_dir, 'national.xls')

            # 校验模板
            val = validator.get_validator()
            validation_result = val.validate_national_template(filepath)

            if validation_result['valid']:
                session['national_file'] = filepath
                return jsonify({
                    'success': True,
                    'valid': True,
                    'message': '文件上传成功，格式校验通过'
                })
            else:
                # 校验失败，删除文件并清除session
                if os.path.exists(filepath):
                    os.remove(filepath)
                session.pop('national_file', None)  # 清除session中的文件路径
                error_msg = '上传表格格式不正确'

                # 添加详细的列位置信息
                if validation_result.get('column_details'):
                    details = validation_result['column_details']
                    error_msg += '：'
                    detail_msgs = []
                    for detail in details[:5]:  # 最多显示前5个差异
                        detail_msgs.append(
                            f"{detail['position']}应为'{detail['expected']}'，实际为'{detail['actual']}'"
                        )
                    error_msg += '；'.join(detail_msgs)
                    if len(details) > 5:
                        error_msg += f'；等共{len(details)}处差异'
                elif validation_result.get('order_mismatch'):
                    error_msg += "，列顺序不匹配"
                elif 'missing_columns' in validation_result and validation_result['missing_columns']:
                    error_msg += f"，缺少列: {', '.join(validation_result['missing_columns'])}"

                if 'error' in validation_result:
                    error_msg = validation_result['error']

                return jsonify({
                    'success': True,
                    'valid': False,
                    'error': error_msg,
                    'column_details': validation_result.get('column_details', [])
                })

        except ValueError as e:
            session.pop('national_file', None)  # 清除session
            return jsonify({'success': False, 'error': str(e)}), 400
        except Exception as e:
            session.pop('national_file', None)  # 清除session
            logger.error(f"上传全国库文件失败: {e}")
            return jsonify({'success': False, 'error': '文件上传失败'}), 500

    @app.route('/compare', methods=['POST'])
    def compare():
        """执行比对"""
        try:
            # 检查是否已上传两个文件
            local_file = session.get('local_file')
            national_file = session.get('national_file')

            if not local_file or not national_file:
                return jsonify({
                    'success': False,
                    'error': '请先上传并校验两个文件'
                }), 400

            # 检查文件是否存在
            if not os.path.exists(local_file):
                session.pop('local_file', None)
                return jsonify({
                    'success': False,
                    'error': '单机库文件不存在，请重新上传'
                }), 400

            if not os.path.exists(national_file):
                session.pop('national_file', None)
                return jsonify({
                    'success': False,
                    'error': '全国库文件不存在，请重新上传'
                }), 400

            # 读取文件
            df_local = pd.read_excel(local_file)
            df_national = pd.read_excel(national_file, sheet_name=0)

            # 执行比对
            engine = comparison.ComparisonEngine(df_local, df_national)
            results = engine.generate_report()

            # 获取会话目录
            session_id = session.get('session_id')
            if not session_id:
                return jsonify({'success': False, 'error': '会话无效'}), 400

            session_dir = os.path.join(
                app.config['UPLOAD_FOLDER'],
                session_id
            )

            # 将比对结果保存到pickle文件
            results_file = os.path.join(session_dir, 'results.pkl')
            with open(results_file, 'wb') as f:
                pickle.dump(results, f)

            # 在session中只存储标志
            session['has_results'] = True
            session.modified = True

            # 清理上传的临时文件
            try:
                if os.path.exists(local_file):
                    os.remove(local_file)
                if os.path.exists(national_file):
                    os.remove(national_file)
            except Exception as e:
                logger.warning(f"清理临时文件失败: {e}")

            return jsonify({'success': True})

        except Exception as e:
            logger.error(f"比对失败: {e}")
            return jsonify({'success': False, 'error': f'比对失败: {str(e)}'}), 500

    @app.route('/result')
    def result():
        """显示比对结果"""
        # 检查是否有比对结果
        if not session.get('has_results'):
            return redirect(url_for('index'))

        # 获取会话目录
        session_id = session.get('session_id')
        if not session_id:
            return redirect(url_for('index'))

        session_dir = os.path.join(
            app.config['UPLOAD_FOLDER'],
            session_id
        )
        results_file = os.path.join(session_dir, 'results.pkl')

        # 从pickle文件读取结果
        if not os.path.exists(results_file):
            return redirect(url_for('index'))

        with open(results_file, 'rb') as f:
            results = pickle.load(f)

        # 将 DataFrame 转换为 HTML 表格
        def df_to_html(df):
            if df is None or (isinstance(df, pd.DataFrame) and df.empty):
                return '<p class="no-data">暂无数据</p>'
            if df.empty:
                return '<p class="no-data">暂无数据</p>'
            return df.to_html(
                classes='result-table',
                index=False,
                escape=False,
                na_rep=''
            )

        # 准备展示数据
        local_extra_df = results.get('local_extra')
        national_extra_df = results.get('national_extra')

        display_data = {
            'local_extra': df_to_html(local_extra_df),
            'local_extra_count': len(local_extra_df) if local_extra_df is not None else 0,
            'national_extra': df_to_html(national_extra_df),
            'national_extra_count': len(national_extra_df) if national_extra_df is not None else 0,
        }

        # 字段差异
        diff_fields = [
            '姓名', '性别', '民族', '出生日期',
            '学历', '入党时间', '个人身份', '人员类别'
        ]

        field_diffs = {}
        for field in diff_fields:
            diff_key = f'diff_{field}'
            df = results.get(diff_key)
            field_diffs[field] = {
                'html': df_to_html(df),
                'count': len(df) if df is not None and not (isinstance(df, pd.DataFrame) and df.empty) else 0
            }

        display_data['field_diffs'] = field_diffs

        # 添加预处理数据表
        local_preprocessed = results.get('local_preprocessed')
        national_preprocessed = results.get('national_preprocessed')

        display_data['local_preprocessed'] = df_to_html(local_preprocessed)
        display_data['local_preprocessed_count'] = len(local_preprocessed) if local_preprocessed is not None else 0

        display_data['national_preprocessed'] = df_to_html(national_preprocessed)
        display_data['national_preprocessed_count'] = len(national_preprocessed) if national_preprocessed is not None else 0

        return render_template('result.html', data=display_data)

    @app.route('/download')
    def download():
        """下载比对结果 Excel 文件"""
        try:
            # 检查是否有比对结果
            if not session.get('has_results'):
                return jsonify({
                    'error': '未找到比对结果，请先执行比对'
                }), 404

            # 获取会话目录
            session_id = session.get('session_id')
            if not session_id:
                return jsonify({'error': '会话无效'}), 400

            session_dir = os.path.join(
                app.config['UPLOAD_FOLDER'],
                session_id
            )
            results_file = os.path.join(session_dir, 'results.pkl')

            # 从pickle文件读取结果
            if not os.path.exists(results_file):
                return jsonify({
                    'error': '未找到比对结果，请先执行比对'
                }), 404

            with open(results_file, 'rb') as f:
                results = pickle.load(f)

            # 导出到 Excel
            filepath = exporter.export_to_excel(results, session_dir)

            # 发送文件
            return send_file(
                filepath,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name=os.path.basename(filepath)
            )

        except Exception as e:
            logger.error(f"下载文件失败: {e}")
            return jsonify({'error': '下载失败'}), 500

    @app.route('/download/template/local')
    def download_local_template():
        """下载单机库标准模板文件"""
        try:
            template_path = os.path.join(
                app.config['TEMPLATES_FOLDER'],
                '单机模板.xls'
            )

            if not os.path.exists(template_path):
                return jsonify({'error': '模板文件不存在'}), 404

            return send_file(
                template_path,
                mimetype='application/vnd.ms-excel',
                as_attachment=True,
                download_name='单机模板.xls'
            )

        except Exception as e:
            logger.error(f"下载单机模板失败: {e}")
            return jsonify({'error': '下载失败'}), 500

    @app.route('/download/template/national')
    def download_national_template():
        """下载全国库标准模板文件"""
        try:
            template_path = os.path.join(
                app.config['TEMPLATES_FOLDER'],
                '全国模板.xls'
            )

            if not os.path.exists(template_path):
                return jsonify({'error': '模板文件不存在'}), 404

            return send_file(
                template_path,
                mimetype='application/vnd.ms-excel',
                as_attachment=True,
                download_name='全国模板.xls'
            )

        except Exception as e:
            logger.error(f"下载全国模板失败: {e}")
            return jsonify({'error': '下载失败'}), 500

    # 错误处理器
    @app.errorhandler(404)
    def not_found(error):
        """404 错误处理"""
        return render_template('404.html'), 404

    @app.errorhandler(413)
    @app.errorhandler(RequestEntityTooLarge)
    def request_entity_too_large(error):
        """文件过大错误处理"""
        return jsonify({
            'success': False,
            'error': '文件大小超过限制(最大 10MB)'
        }), 413

    @app.errorhandler(500)
    def internal_error(error):
        """500 错误处理"""
        logger.error(f"内部错误: {error}")
        return jsonify({'error': '服务器内部错误'}), 500
