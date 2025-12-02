import openai
import json
from config import Config
import httpx
import re
from services.cache_service import get_cached_description, set_cached_description

# 配置OpenAI客户端以使用DeepSeek
client = openai.OpenAI(
    api_key=Config.DEEPSEEK_API_KEY,
    base_url=Config.DEEPSEEK_BASE_URL,
    http_client=httpx.Client(timeout=60.0)
)

def fix_json_common_issues(json_str):
    """
    尝试修复常见的JSON格式问题：
    1. 在数组或对象末尾添加缺失的逗号（当后面跟着新字段时）
    2. 移除对象或数组中的尾随逗号
    3. 修复未转义的双引号（简单处理）
    """
    # 修复：在 ']' 后缺少逗号，后面跟着 '"'
    # 模式：]\\s*\"   => 在 ] 和 " 之间插入逗号
    import re
    fixed = re.sub(r'\]\s*\"', '], "', json_str)
    # 修复：在 '}' 后缺少逗号，后面跟着 '"'
    fixed = re.sub(r'\}\s*\"', '}, "', fixed)
    # 移除对象中的尾随逗号（如 ,\s*} -> }）
    fixed = re.sub(r',\s*}', '}', fixed)
    # 移除数组中的尾随逗号（如 ,\s*] -> ]）
    fixed = re.sub(r',\s*]', ']', fixed)
    # 修复未闭合的字符串（简单处理：忽略）
    return fixed

def generate_workout_plan(profile):
    """
    根据用户资料生成周锻炼计划
    profile: 用户资料字典
    返回: JSON字符串格式的周计划
    """
    # 构建提示
    prompt = build_prompt(profile)
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一位专业的健身教练，擅长为瘦子（外胚型）设计增重增肌的锻炼计划。请根据用户信息生成一份为期一周的锻炼计划，以JSON格式输出。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            response_format={
                'type': 'json_object'
            },
            max_tokens=2000,
            stream=False,
        )
        content = response.choices[0].message.content
        print(f"DeepSeek API原始响应: {content[:500]}...")  # 打印前500字符
        # 提取JSON部分
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            json_str = json_match.group()
            print(f"提取的JSON字符串 (长度 {len(json_str)}): {json_str[:200]}...")
            # 尝试修复常见JSON问题
            fixed = fix_json_common_issues(json_str)
            # 验证JSON
            try:
                parsed = json.loads(fixed)
                print("JSON解析成功（修复后）")
                return fixed
            except json.JSONDecodeError as je:
                print(f"JSON解析失败（修复后）: {je}")
                print(f"有问题的JSON片段: {fixed[je.pos-50:je.pos+50]}")
                # 返回默认计划
                return get_default_plan(profile)
        else:
            print("未找到JSON结构，使用默认计划")
            # 如果没找到JSON，返回一个默认计划
            return get_default_plan(profile)
    except Exception as e:
        import traceback
        print(f"DeepSeek API错误详情:")
        print(f"异常类型: {type(e).__name__}")
        print(f"异常消息: {str(e)}")
        traceback.print_exc()
        # 如果是httpx或openai错误，尝试获取更多信息
        if hasattr(e, 'response'):
            try:
                print(f"响应状态码: {e.response.status_code}")
                print(f"响应内容: {e.response.text}")
            except:
                pass
        return get_default_plan(profile)

def build_prompt(profile):
    """构建提示文本"""
    equipment = profile.get('available_equipment', [])
    if isinstance(equipment, list):
        equipment_str = '、'.join(equipment) if equipment else '无器械（自重训练）'
    else:
        equipment_str = str(equipment)
    prompt = f"""
用户信息：
- 年龄：{profile.get('age', '未提供')}
- 身高：{profile.get('height_cm', '未提供')} cm
- 当前体重：{profile.get('current_weight_kg', '未提供')} kg
- 目标体重：{profile.get('target_weight_kg', '未提供')} kg
- 体脂率：{profile.get('body_fat_percent', '未提供')}%
- 训练经验：{profile.get('training_experience', 'beginner')}
- 可用器械：{equipment_str}
- 每周训练天数：{profile.get('preferences', {}).get('days_per_week', 3)}
- 每次训练时长：{profile.get('preferences', {}).get('session_minutes', 60)} 分钟
- 重点部位：{', '.join(profile.get('preferences', {}).get('focus', ['全身']))}
- 避免：{profile.get('preferences', {}).get('avoid', '无')}

请生成一份为期7天的锻炼计划，每天包含：
1. 训练部位
2. 具体动作（名称、组数、次数、重量建议）
3. 休息时间
4. 训练提示

以JSON格式输出，结构如下：
{{
  "days": [
    {{
      "day": 1,
      "focus": "胸部、三头肌",
      "exercises": [
        {{
          "name": "卧推",
          "sets": 3,
          "reps": "8-12",
          "weight": "适中",
          "rest": "60-90秒"
        }}
      ],
      "tips": "保持动作规范，注意肩部稳定。"
    }}
  ]
}}
"""
    return prompt

def get_default_plan(profile):
    """返回一个默认计划（当API失败时）"""
    days = []
    focus_areas = [
        "胸部、三头肌",
        "背部、二头肌",
        "腿部、肩部",
        "全身",
        "核心、有氧",
        "休息",
        "活动恢复"
    ]
    for i in range(7):
        days.append({
            "day": i+1,
            "focus": focus_areas[i],
            "exercises": [
                {
                    "name": "示例动作",
                    "sets": 3,
                    "reps": "10-15",
                    "weight": "自重或轻重量",
                    "rest": "60秒"
                }
            ],
            "tips": "根据自身感受调整强度。"
        })
    return json.dumps({"days": days}, ensure_ascii=False)
def generate_exercise_description(exercise_name, user_profile):
    """
    生成运动的详细介绍，使用缓存避免重复调用API。
    exercise_name: 运动名称（字符串）
    user_profile: 用户资料字典（包含user_id等）
    返回: (介绍文本, 是否缓存)
    """
    # 首先检查缓存
    cached = get_cached_description(exercise_name, user_profile)
    if cached is not None:
        print(f"[INFO] 使用缓存的运动介绍: {exercise_name}")
        return cached, True

    print(f"[INFO] 调用DeepSeek API生成运动介绍: {exercise_name}")
    # 构建提示
    equipment = user_profile.get('available_equipment', [])
    if isinstance(equipment, list):
        equipment_str = '、'.join(equipment) if equipment else '无器械（自重训练）'
    else:
        equipment_str = str(equipment)

    prompt = f"""
你是一位专业的健身教练，擅长为瘦子（外胚型）设计增重增肌的锻炼计划。
请为以下运动提供详细、专业的介绍，包括：
1. 动作要领（标准姿势、常见错误）
2. 目标肌肉群
3. 适合的训练阶段（初学者/中级/高级）
4. 变式动作（如果有）
5. 安全注意事项
6. 与该用户个人情况的结合建议（根据用户资料）

用户信息：
- 年龄：{user_profile.get('age', '未提供')}
- 身高：{user_profile.get('height_cm', '未提供')} cm
- 当前体重：{user_profile.get('current_weight_kg', '未提供')} kg
- 目标体重：{user_profile.get('target_weight_kg', '未提供')} kg
- 训练经验：{user_profile.get('training_experience', 'beginner')}
- 可用器械：{equipment_str}

请针对运动「{exercise_name}」提供详细介绍。
请用中文回答，语言亲切、专业，段落清晰。
"""
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一位专业的健身教练，擅长为瘦子（外胚型）设计增重增肌的锻炼计划。请根据用户信息提供运动的详细介绍。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1500
        )
        content = response.choices[0].message.content.strip()
        # 存入缓存
        set_cached_description(exercise_name, user_profile, content)
        return content, False
    except Exception as e:
        import traceback
        print(f"DeepSeek API错误（生成运动介绍）: {e}")
        traceback.print_exc()
        # 返回一个默认介绍
        default_desc = f"""
运动名称：{exercise_name}

动作要领：请保持标准姿势，注意控制节奏。
目标肌肉群：根据动作而定。
适合阶段：初学者。
安全注意事项：避免重量过大导致受伤。
结合建议：根据您的个人情况，建议从轻重量开始，逐渐增加强度。
"""
        return default_desc, False