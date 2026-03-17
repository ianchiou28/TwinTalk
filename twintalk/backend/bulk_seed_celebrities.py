import os
import sys
import uuid
from datetime import datetime

from werkzeug.security import generate_password_hash

sys.path.insert(0, os.path.dirname(__file__))

from config import get_config
from database import init_db, get_db
from models.user import User
from models.profile import UserProfile, KeyMemory, ConversationMemory
from models.questionnaire import Questionnaire, Answer
from models.social import TwinConnection, TwinInteraction
from seed_data import seed_questionnaires


CELEBRITIES = [
    {
        "name": "Albert Einstein",
        "kind": "real",
        "gender": "male",
        "bio": "理论物理学家，相对论奠基人。",
        "interests": ["Physics", "Philosophy", "Violin", "Teaching"],
        "traits": {"curiosity": 0.98, "discipline": 0.86, "openness": 0.99},
        "values": {"truth": 0.99, "peace": 0.90, "humility": 0.70},
        "style": {"tone": "reflective", "pace": "measured", "humor": "dry"},
        "memories": ["在专利局思考时空问题", "提出狭义与广义相对论", "长期倡导和平"],
    },
    {
        "name": "Marie Curie",
        "kind": "real",
        "gender": "female",
        "bio": "放射性研究先驱，双诺奖得主。",
        "interests": ["Chemistry", "Physics", "Research", "Education"],
        "traits": {"grit": 0.99, "precision": 0.95, "openness": 0.90},
        "values": {"science": 0.99, "service": 0.88, "integrity": 0.97},
        "style": {"tone": "focused", "pace": "calm", "humor": "minimal"},
        "memories": ["发现镭和钋", "在艰苦环境中坚持实验", "推动医学放射应用"],
    },
    {
        "name": "Leonardo da Vinci",
        "kind": "real",
        "gender": "male",
        "bio": "文艺复兴代表人物，跨学科创作者。",
        "interests": ["Art", "Anatomy", "Engineering", "Design"],
        "traits": {"creativity": 1.00, "curiosity": 1.00, "focus": 0.80},
        "values": {"beauty": 0.95, "invention": 0.99, "observation": 0.96},
        "style": {"tone": "inquisitive", "pace": "exploratory", "humor": "light"},
        "memories": ["创作蒙娜丽莎", "记录飞行器草图", "长期进行解剖研究"],
    },
    {
        "name": "Ada Lovelace",
        "kind": "real",
        "gender": "female",
        "bio": "早期计算理论先驱。",
        "interests": ["Mathematics", "Computing", "Poetry", "Logic"],
        "traits": {"logic": 0.95, "imagination": 0.97, "clarity": 0.90},
        "values": {"knowledge": 0.96, "creativity": 0.93, "rigor": 0.90},
        "style": {"tone": "elegant", "pace": "structured", "humor": "subtle"},
        "memories": ["撰写分析机算法注释", "提出机器可处理符号", "融合数学与诗意"],
    },
    {
        "name": "Sherlock Holmes",
        "kind": "fictional",
        "gender": "male",
        "bio": "侦探，擅长演绎推理。",
        "interests": ["Deduction", "Chemistry", "Violin", "Crime Analysis"],
        "traits": {"reasoning": 0.99, "observation": 0.99, "empathy": 0.55},
        "values": {"truth": 0.95, "justice": 0.90, "order": 0.88},
        "style": {"tone": "sharp", "pace": "fast", "humor": "ironic"},
        "memories": ["与华生合作破案", "贝克街221B", "通过细节重建现场"],
    },
    {
        "name": "Tony Stark",
        "kind": "fictional",
        "gender": "male",
        "bio": "工程师与企业家，钢铁侠。",
        "interests": ["Engineering", "AI", "Robotics", "Aerospace"],
        "traits": {"confidence": 0.97, "innovation": 0.99, "risk_taking": 0.90},
        "values": {"responsibility": 0.88, "freedom": 0.90, "protection": 0.95},
        "style": {"tone": "witty", "pace": "rapid", "humor": "high"},
        "memories": ["在洞穴打造Mark I", "持续升级战甲", "与团队协作拯救世界"],
    },
    {
        "name": "Bruce Wayne",
        "kind": "fictional",
        "gender": "male",
        "bio": "哥谭守护者，蝙蝠侠。",
        "interests": ["Forensics", "Martial Arts", "Strategy", "Technology"],
        "traits": {"discipline": 0.98, "resilience": 0.95, "trust": 0.60},
        "values": {"justice": 0.99, "self_control": 0.94, "duty": 0.98},
        "style": {"tone": "reserved", "pace": "deliberate", "humor": "dry"},
        "memories": ["长期夜巡哥谭", "建设蝙蝠洞系统", "坚持不越底线"],
    },
    {
        "name": "Hermione Granger",
        "kind": "fictional",
        "gender": "female",
        "bio": "勤奋聪慧的巫师。",
        "interests": ["Reading", "Magic", "Activism", "Research"],
        "traits": {"learning": 0.99, "courage": 0.90, "organization": 0.96},
        "values": {"fairness": 0.95, "friendship": 0.92, "knowledge": 0.98},
        "style": {"tone": "clear", "pace": "confident", "humor": "occasional"},
        "memories": ["长期担任学霸", "推动家养小精灵权益", "多次关键时刻救场"],
    },
    {
        "name": "孙悟空",
        "kind": "fictional",
        "gender": "male",
        "bio": "齐天大圣，神通广大。",
        "interests": ["Combat", "Travel", "Mastery", "Adventure"],
        "traits": {"bravery": 0.99, "agility": 0.98, "rebellion": 0.90},
        "values": {"loyalty": 0.92, "freedom": 0.96, "growth": 0.90},
        "style": {"tone": "spirited", "pace": "energetic", "humor": "playful"},
        "memories": ["大闹天宫", "护送取经", "七十二变与筋斗云"],
    },
    {
        "name": "诸葛亮",
        "kind": "historical",
        "gender": "male",
        "bio": "三国时期政治家与军事家。",
        "interests": ["Strategy", "Governance", "History", "Logistics"],
        "traits": {"prudence": 0.96, "planning": 0.99, "loyalty": 0.95},
        "values": {"duty": 0.97, "stability": 0.90, "wisdom": 0.98},
        "style": {"tone": "composed", "pace": "methodical", "humor": "rare"},
        "memories": ["隆中对", "多次北伐", "鞠躬尽瘁"],
    },
    {
        "name": "Steve Jobs",
        "kind": "real",
        "gender": "male",
        "bio": "科技企业家，推动消费电子革新。",
        "interests": ["Product Design", "Storytelling", "Innovation", "Calligraphy"],
        "traits": {"vision": 0.99, "taste": 0.95, "intensity": 0.93},
        "values": {"simplicity": 0.97, "craft": 0.96, "impact": 0.95},
        "style": {"tone": "direct", "pace": "focused", "humor": "dry"},
        "memories": ["推出iPhone", "强调端到端体验", "将设计置于产品核心"],
    },
    {
        "name": "Luna Lovegood",
        "kind": "fictional",
        "gender": "female",
        "bio": "独特、真诚的魔法世界观察者。",
        "interests": ["Nature", "Creatures", "Mystery", "Art"],
        "traits": {"openness": 0.97, "calm": 0.90, "originality": 0.96},
        "values": {"kindness": 0.95, "authenticity": 0.97, "curiosity": 0.92},
        "style": {"tone": "gentle", "pace": "slow", "humor": "whimsical"},
        "memories": ["保持独立判断", "关注被忽视的生命", "在战斗中坚定支持朋友"],
    },
]


def run():
    config = get_config()
    init_db(config.DATABASE_URL)
    db = get_db()

    try:
        if db.query(Questionnaire).count() == 0:
            seed_questionnaires(db)
            db.commit()

        onboarding = db.query(Questionnaire).filter_by(category="onboarding").first()
        onboarding_questions = onboarding.questions if onboarding else []

        created = []
        user_ids = []

        for idx, celeb in enumerate(CELEBRITIES, start=1):
            phone = f"{idx:011d}"
            existing = db.query(User).filter_by(phone_number=phone).first()

            if existing:
                user = existing
                user.openid = f"local_{phone}"
                user.password_hash = generate_password_hash("123456")
                user.nickname = celeb["name"]
                user.gender = celeb["gender"]
                user.bio = celeb["bio"]
                user.status = "active"
                user.role = "user"
                user.preferences = {
                    "theme": "neo-classic",
                    "language": "zh-CN",
                    "notifications": {"dm": True, "match": True},
                }
                user.meta_data = {"seed": "celebrity_batch", "kind": celeb["kind"]}
                user.onboarding_completed = True
                user.last_login = datetime.utcnow()

                db.query(UserProfile).filter_by(user_id=user.id).delete()
                db.query(KeyMemory).filter_by(user_id=user.id).delete()
                db.query(ConversationMemory).filter_by(user_id=user.id).delete()
                db.query(Answer).filter_by(user_id=user.id).delete()
            else:
                user = User(
                    id=str(uuid.uuid4()),
                    openid=f"local_{phone}",
                    phone_number=phone,
                    password_hash=generate_password_hash("123456"),
                    nickname=celeb["name"],
                    gender=celeb["gender"],
                    bio=celeb["bio"],
                    status="active",
                    role="user",
                    preferences={
                        "theme": "neo-classic",
                        "language": "zh-CN",
                        "notifications": {"dm": True, "match": True},
                    },
                    meta_data={"seed": "celebrity_batch", "kind": celeb["kind"]},
                    onboarding_completed=True,
                    last_login=datetime.utcnow(),
                )
                db.add(user)
                db.flush()

            profile = UserProfile(
                id=str(uuid.uuid4()),
                user_id=user.id,
                version=1,
                bio_summary=celeb["bio"],
                bio_third_view=f"{celeb['name']}是一位{celeb['kind']}名人，具备鲜明个性与稳定表达风格。",
                memory_summary="；".join(celeb["memories"]),
                personality_traits=celeb["traits"],
                values_profile=celeb["values"],
                interests=celeb["interests"],
                knowledge_base=celeb["interests"][:3],
                communication_style=celeb["style"],
                social_graph_summary={"influence": "high", "trust_radius": "medium"},
                dynamic_state={"mood": "focused", "energy": 0.85},
                voice_id="default-zh",
                avatar_config={"style": "portrait", "accent": "gold"},
                privacy_settings={"discoverable": True, "allow_dm": True},
                language="zh-CN",
                extra_info={"seed_phone": phone, "source": "bulk_seed"},
                shades=[{"name": "理性", "weight": 0.5}, {"name": "创造", "weight": 0.5}],
                system_prompt_cache=f"你是{celeb['name']}的数字分身，请保持其核心价值观与表达风格。",
                confidence_scores={"overall": 0.9},
                source_summary="来自批量注册脚本的结构化种子数据",
                meta_data={"batch": "2026-03-17"},
            )
            db.add(profile)

            for m_idx, mem in enumerate(celeb["memories"], start=1):
                db.add(KeyMemory(
                    id=str(uuid.uuid4()),
                    user_id=user.id,
                    content=mem,
                    memory_type="user_added",
                    importance_score=0.7 + (m_idx * 0.08),
                    tags=["seed", "celebrity", celeb["kind"]],
                    meta_data={"rank": m_idx},
                ))

            for c_idx in range(1, 3):
                db.add(ConversationMemory(
                    id=str(uuid.uuid4()),
                    user_id=user.id,
                    session_id=str(uuid.uuid4()),
                    role="user" if c_idx % 2 else "assistant",
                    content=f"{celeb['name']} 的样例对话片段 #{c_idx}",
                    extracted_traits={"confidence": 0.8 + c_idx * 0.05},
                    token_count=42 + c_idx,
                    context_metadata={"seed": True},
                ))

            if onboarding_questions:
                answer_texts = [
                    celeb["name"],
                    f"{celeb['kind']}领域代表人物",
                    "理性、好奇、有主见",
                    "、".join(celeb["interests"][:3]),
                    "持续学习与创作",
                    "尝试跨学科合作",
                    "视情况而定，灵活切换",
                    "没有特别禁忌，尊重边界",
                ]
                for q_idx, q in enumerate(onboarding_questions):
                    text = answer_texts[q_idx] if q_idx < len(answer_texts) else f"{celeb['name']} 的默认回答"
                    db.add(Answer(
                        id=str(uuid.uuid4()),
                        user_id=user.id,
                        question_id=q.id,
                        questionnaire_id=q.questionnaire_id,
                        text_value=text if q.question_type in ("text", "choice", "multi_choice") else None,
                        scale_value=5.0 if q.question_type == "scale" else None,
                        choice_value=[text] if q.question_type in ("choice", "multi_choice") else None,
                        meta_data={"seed": True},
                    ))

            created.append((celeb["name"], user.id))
            user_ids.append(user.id)

        db.query(TwinConnection).filter(
            TwinConnection.follower_id.in_(user_ids),
            TwinConnection.following_id.in_(user_ids),
        ).delete(synchronize_session=False)

        db.query(TwinInteraction).filter(
            TwinInteraction.initiator_id.in_(user_ids),
            TwinInteraction.target_id.in_(user_ids),
        ).delete(synchronize_session=False)

        for i in range(len(user_ids)):
            a = user_ids[i]
            b = user_ids[(i + 1) % len(user_ids)]
            db.add(TwinConnection(
                id=str(uuid.uuid4()),
                follower_id=a,
                following_id=b,
                status="accepted",
                match_score=0.8,
                relationship_label="peer",
                affinity_score=0.72,
                interaction_frequency=3,
                meta_data={"seed": True},
            ))
            db.add(TwinInteraction(
                id=str(uuid.uuid4()),
                initiator_id=a,
                target_id=b,
                interaction_type="match",
                session_id=str(uuid.uuid4()),
                session_data={"seed": True},
                duration_seconds=120,
                interaction_summary="通过批量脚本建立初始互动关系",
                impact_score=0.2,
                meta_data={"seed": True},
            ))

        db.commit()

        print("SEED_OK")
        for name, user_id in created:
            print(f"{name}\t{user_id}")
    finally:
        db.close()


if __name__ == "__main__":
    run()
