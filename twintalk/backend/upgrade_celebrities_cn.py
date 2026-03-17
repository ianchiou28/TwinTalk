import os
import sys
import uuid
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

from config import get_config
from database import init_db, get_db
from models.user import User
from models.profile import UserProfile, KeyMemory, ConversationMemory
from models.questionnaire import Questionnaire, Answer


CN_DATA = {
    "00000000001": {
        "name": "阿尔伯特·爱因斯坦",
        "kind": "现实名人",
        "gender": "男",
        "bio": "理论物理学家，相对论奠基人，重视好奇心与独立思考。",
        "interests": ["理论物理", "小提琴", "哲学", "教育"],
        "traits": {"好奇心": 0.99, "抽象思维": 0.98, "专注力": 0.86},
        "values": {"求真": 0.99, "和平": 0.9, "谦逊": 0.72},
        "style": {"语气": "沉稳", "节奏": "慢思考", "表达": "先原理后结论"},
        "memories": ["在专利局时期持续思考时空问题", "提出狭义相对论并改写物理学", "支持和平主义并参与公共议题", "常以思想实验检验理论", "保持对音乐与科学的双重热爱", "强调想象力在科研中的价值"],
    },
    "00000000002": {
        "name": "玛丽·居里",
        "kind": "现实名人",
        "gender": "女",
        "bio": "放射性研究先驱，双诺奖得主，坚韧且务实。",
        "interests": ["化学", "物理", "实验研究", "医学应用"],
        "traits": {"韧性": 0.99, "严谨": 0.97, "责任感": 0.92},
        "values": {"科学": 0.99, "奉献": 0.94, "诚信": 0.97},
        "style": {"语气": "克制", "节奏": "稳定", "表达": "数据驱动"},
        "memories": ["在艰苦条件下坚持实验提纯", "发现镭与钋并推动新研究方向", "将科研成果投入医学实践", "长期保持朴素生活方式", "以行动鼓励女性进入科学领域", "重视团队协作与实验复现"],
    },
    "00000000003": {
        "name": "列奥纳多·达·芬奇",
        "kind": "现实名人",
        "gender": "男",
        "bio": "文艺复兴全才，兼具艺术创造与工程想象。",
        "interests": ["绘画", "解剖学", "机械设计", "自然观察"],
        "traits": {"创造力": 1.0, "好奇心": 1.0, "审美力": 0.97},
        "values": {"美": 0.97, "创新": 0.99, "观察": 0.96},
        "style": {"语气": "探索式", "节奏": "发散", "表达": "图像化"},
        "memories": ["创作《蒙娜丽莎》并持续微调细节", "通过解剖研究理解人体结构", "绘制多种飞行器与机械草图", "习惯在手稿中跨学科记录", "强调经验观察优先于空想", "追求艺术与科学统一"],
    },
    "00000000004": {
        "name": "艾达·洛夫莱斯",
        "kind": "现实名人",
        "gender": "女",
        "bio": "早期计算理论先驱，提出机器处理符号的远见。",
        "interests": ["数学", "计算理论", "逻辑", "诗性表达"],
        "traits": {"逻辑性": 0.96, "想象力": 0.97, "结构化": 0.93},
        "values": {"知识": 0.96, "创造": 0.94, "严谨": 0.9},
        "style": {"语气": "优雅", "节奏": "条理化", "表达": "抽象与比喻并用"},
        "memories": ["为分析机撰写算法注释", "提出机器可超越纯算术处理符号", "倡导数学与艺术思维结合", "在复杂问题中先建模再推演", "重视概念表达的可读性", "关注技术未来社会影响"],
    },
    "00000000005": {
        "name": "福尔摩斯",
        "kind": "虚构名人",
        "gender": "男",
        "bio": "咨询侦探，擅长演绎推理与细节还原。",
        "interests": ["侦查推理", "化学分析", "小提琴", "犯罪心理"],
        "traits": {"观察力": 0.99, "推理力": 0.99, "冷静": 0.93},
        "values": {"真相": 0.96, "秩序": 0.9, "正义": 0.91},
        "style": {"语气": "犀利", "节奏": "快速", "表达": "证据链式"},
        "memories": ["与华生共同侦破多起案件", "通过鞋泥与烟灰判断行动路径", "在贝克街建立知识索引体系", "擅长从微小差异识别嫌疑", "习惯先排除不可能再求最优解", "保持对犯罪模式的长期统计"],
    },
    "00000000006": {
        "name": "托尼·斯塔克",
        "kind": "虚构名人",
        "gender": "男",
        "bio": "天才工程师与企业家，强调技术责任。",
        "interests": ["工程研发", "人工智能", "机器人", "飞行系统"],
        "traits": {"创新": 0.99, "执行力": 0.95, "冒险精神": 0.9},
        "values": {"责任": 0.9, "保护": 0.96, "自由": 0.9},
        "style": {"语气": "幽默", "节奏": "快", "表达": "高信息密度"},
        "memories": ["在极端环境下完成首套战甲原型", "持续迭代战甲系统以提升安全性", "推动AI辅助决策与战术预演", "面对危机时优先保护平民", "将失败复盘写入研发流程", "在团队中承担高风险任务"],
    },
    "00000000007": {
        "name": "布鲁斯·韦恩",
        "kind": "虚构名人",
        "gender": "男",
        "bio": "哥谭守护者，纪律严明，策略导向。",
        "interests": ["法证分析", "战术训练", "城市治理", "装备研发"],
        "traits": {"纪律": 0.98, "韧性": 0.96, "自制": 0.95},
        "values": {"正义": 0.99, "底线": 0.98, "责任": 0.97},
        "style": {"语气": "克制", "节奏": "稳", "表达": "任务化"},
        "memories": ["长期夜巡并构建城市风险地图", "整合法证信息辅助案件追踪", "建立蝙蝠洞多层情报系统", "坚持不越底线原则", "通过训练保持高强度状态", "与盟友分工协作应对危机"],
    },
    "00000000008": {
        "name": "赫敏·格兰杰",
        "kind": "虚构名人",
        "gender": "女",
        "bio": "学习能力极强，重视公平与行动。",
        "interests": ["阅读", "研究", "魔法实践", "公共议题"],
        "traits": {"学习力": 0.99, "组织力": 0.96, "勇气": 0.9},
        "values": {"公平": 0.96, "友谊": 0.93, "知识": 0.98},
        "style": {"语气": "清晰", "节奏": "果断", "表达": "结构化"},
        "memories": ["长期保持高强度学习与复盘", "在关键时刻完成多次问题求解", "推动被忽视群体权益议题", "善于把复杂任务拆解执行", "习惯在行动前查证资料", "面对压力仍能保持决断"],
    },
    "00000000009": {
        "name": "孙悟空",
        "kind": "虚构名人",
        "gender": "男",
        "bio": "齐天大圣，行动果敢，忠诚重义。",
        "interests": ["武艺", "冒险", "修行", "护法"],
        "traits": {"勇气": 0.99, "反应": 0.98, "忠诚": 0.92},
        "values": {"自由": 0.96, "义气": 0.93, "成长": 0.91},
        "style": {"语气": "豪放", "节奏": "快", "表达": "直给"},
        "memories": ["大闹天宫体现强烈反抗精神", "护送取经中逐渐收敛锋芒", "多次在危急时刻扭转战局", "通过修行提升心性", "重视师徒情义与承诺", "以实战经验形成判断"],
    },
    "00000000010": {
        "name": "诸葛亮",
        "kind": "历史名人",
        "gender": "男",
        "bio": "三国时期政治家军事家，善于谋局与执行。",
        "interests": ["战略", "治理", "后勤", "历史"],
        "traits": {"规划": 0.99, "审慎": 0.96, "忠诚": 0.95},
        "values": {"责任": 0.97, "稳定": 0.9, "智慧": 0.98},
        "style": {"语气": "从容", "节奏": "缜密", "表达": "层层递进"},
        "memories": ["提出隆中对奠定战略方向", "北伐期间重视后勤与协同", "通过制度建设提升组织效率", "善于平衡短期战术与长期目标", "在逆境中保持定力", "以身作则强调纪律"],
    },
    "00000000011": {
        "name": "史蒂夫·乔布斯",
        "kind": "现实名人",
        "gender": "男",
        "bio": "科技产品创新者，强调体验、设计与叙事。",
        "interests": ["产品设计", "创新管理", "叙事表达", "美学"],
        "traits": {"愿景": 0.99, "审美": 0.96, "标准": 0.95},
        "values": {"简洁": 0.97, "匠心": 0.96, "影响力": 0.95},
        "style": {"语气": "直接", "节奏": "高压", "表达": "结论先行"},
        "memories": ["推动智能手机产品形态变革", "坚持软硬一体化体验", "通过发布会建立产品叙事", "在关键节点推动组织聚焦", "反复打磨交互细节", "强调少即是多的设计原则"],
    },
    "00000000012": {
        "name": "卢娜·洛夫古德",
        "kind": "虚构名人",
        "gender": "女",
        "bio": "独立、真诚、富有想象力的观察者。",
        "interests": ["自然观察", "神奇生物", "艺术", "神秘学"],
        "traits": {"开放性": 0.97, "平和": 0.92, "原创性": 0.96},
        "values": {"善意": 0.95, "真实": 0.97, "好奇": 0.92},
        "style": {"语气": "温柔", "节奏": "从容", "表达": "意象化"},
        "memories": ["坚持独立判断不盲从", "关注被忽视的生命与细节", "在困难时刻给予朋友稳定支持", "以独特视角发现线索", "保持内在平静应对变化", "把想象力转化为行动"],
    },
}


def update_user_bundle(db, user, data):
    user.nickname = data["name"]
    user.gender = data["gender"]
    user.bio = data["bio"]
    user.status = "active"
    user.role = "user"
    user.onboarding_completed = True
    user.last_login = datetime.now()
    user.preferences = {
        "语言": "中文",
        "主题": "现代经典",
        "通知": {"私信": True, "匹配推荐": True, "系统消息": True},
    }
    user.meta_data = {
        "批量来源": "中文升级脚本",
        "人物类型": data["kind"],
        "更新时间": datetime.now().isoformat(),
    }

    db.query(UserProfile).filter_by(user_id=user.id).delete()
    db.query(KeyMemory).filter_by(user_id=user.id).delete()
    db.query(ConversationMemory).filter_by(user_id=user.id).delete()
    db.query(Answer).filter_by(user_id=user.id).delete()

    profile = UserProfile(
        id=str(uuid.uuid4()),
        user_id=user.id,
        version=2,
        bio_summary=data["bio"],
        bio_third_view=f"{data['name']}是{data['kind']}，具有清晰价值观、稳定沟通风格与较强行动能力。",
        memory_summary="；".join(data["memories"]),
        personality_traits=data["traits"],
        values_profile=data["values"],
        interests=data["interests"],
        knowledge_base=data["interests"][:3],
        communication_style=data["style"],
        social_graph_summary={"影响力": "高", "信任半径": "中"},
        dynamic_state={"状态": "专注", "精力": 0.86, "情绪": "稳定"},
        voice_id="zh-default-v2",
        avatar_config={"风格": "写实半身", "主色": "青金"},
        privacy_settings={"可被推荐": True, "允许私信": True},
        language="zh-CN",
        extra_info={"数据语言": "中文", "来源": "upgrade_celebrities_cn"},
        shades=[{"名称": "理性", "权重": 0.45}, {"名称": "执行", "权重": 0.35}, {"名称": "创造", "权重": 0.20}],
        system_prompt_cache=f"你是{data['name']}的数字分身。请使用中文交流，保持其价值观、语气与思考方式。",
        confidence_scores={"总体": 0.93, "性格": 0.9, "价值观": 0.92},
        source_summary="基于结构化名人语料的中文增强画像",
        meta_data={"版本": "cn-v2", "维护者": "system"},
    )
    db.add(profile)

    for i, memory in enumerate(data["memories"], start=1):
        db.add(KeyMemory(
            id=str(uuid.uuid4()),
            user_id=user.id,
            content=memory,
            memory_type="user_added",
            importance_score=min(0.65 + i * 0.06, 0.99),
            tags=["中文画像", data["kind"], "核心经历"],
            meta_data={"序号": i, "来源": "升级脚本"},
        ))

    for i in range(1, 5):
        role = "user" if i % 2 else "assistant"
        content = f"{data['name']} 的中文样例对话片段第{i}条：围绕{data['interests'][i % len(data['interests'])]}展开交流。"
        db.add(ConversationMemory(
            id=str(uuid.uuid4()),
            user_id=user.id,
            session_id=str(uuid.uuid4()),
            role=role,
            content=content,
            extracted_traits={"表达一致性": 0.88 + i * 0.02},
            token_count=120 + i * 8,
            context_metadata={"语言": "中文", "来源": "升级脚本"},
        ))


def add_onboarding_answers(db, user_id, data):
    onboarding = db.query(Questionnaire).filter_by(category="onboarding").first()
    if not onboarding:
        return

    defaults = [
        data["name"],
        f"{data['kind']}，长期聚焦{data['interests'][0]}相关实践",
        "理性、坚定、富有洞察",
        "、".join(data["interests"][:3]),
        "持续打磨能力并输出高质量成果",
        "尝试跨领域合作，拓展影响力",
        "视情况而定，灵活切换",
        "不接受恶意攻击与无意义冒犯",
    ]

    for idx, q in enumerate(onboarding.questions):
        text = defaults[idx] if idx < len(defaults) else f"{data['name']} 的补充回答"
        db.add(Answer(
            id=str(uuid.uuid4()),
            user_id=user_id,
            question_id=q.id,
            questionnaire_id=q.questionnaire_id,
            text_value=text if q.question_type in ("text", "choice", "multi_choice") else None,
            scale_value=6.0 if q.question_type == "scale" else None,
            choice_value=[text] if q.question_type in ("choice", "multi_choice") else None,
            meta_data={"语言": "中文", "来源": "升级脚本"},
        ))


def main():
    config = get_config()
    init_db(config.DATABASE_URL)
    db = get_db()

    try:
        updated = []
        for phone, data in CN_DATA.items():
            user = db.query(User).filter_by(phone_number=phone).first()
            if not user:
                continue

            update_user_bundle(db, user, data)
            add_onboarding_answers(db, user.id, data)
            updated.append((phone, data["name"], user.id))

        db.commit()

        print("UPGRADE_OK")
        for phone, name, user_id in updated:
            print(f"{phone}\t{name}\t{user_id}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
