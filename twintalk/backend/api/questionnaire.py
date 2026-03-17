"""Questionnaire API — CRUD, submission, and answer retrieval."""

import uuid
from flask import Blueprint, request, jsonify
from database import get_db
from models.questionnaire import Questionnaire, Question, Answer

questionnaire_bp = Blueprint("questionnaire", __name__, url_prefix="/api/questionnaires")


@questionnaire_bp.route("", methods=["GET"])
def list_questionnaires():
    """获取所有可用问卷列表。"""
    db = get_db()
    try:
        questionnaires = (
            db.query(Questionnaire)
            .filter_by(is_active=True)
            .order_by(Questionnaire.order_index)
            .all()
        )
        return jsonify({
            "success": True,
            "questionnaires": [q.to_dict() for q in questionnaires],
        })
    finally:
        db.close()


@questionnaire_bp.route("/<questionnaire_id>", methods=["GET"])
def get_questionnaire(questionnaire_id):
    """获取问卷详情（含所有题目）。"""
    db = get_db()
    try:
        q = db.query(Questionnaire).filter_by(id=questionnaire_id).first()
        if not q:
            return jsonify({"error": "Questionnaire not found"}), 404
        return jsonify({
            "success": True,
            "questionnaire": q.to_dict(include_questions=True),
        })
    finally:
        db.close()


@questionnaire_bp.route("/<questionnaire_id>/submit", methods=["POST"])
def submit_answers(questionnaire_id):
    """提交问卷回答。
    
    Body: {
        "answers": [
            {"question_id": "...", "scale_value": 5, "text_value": "..."},
            ...
        ]
    }
    """
    user_id = request.headers.get("X-User-Id")
    if not user_id:
        return jsonify({"error": "X-User-Id header required"}), 401

    data = request.get_json()
    answers_data = data.get("answers", [])

    if not answers_data:
        return jsonify({"error": "No answers provided"}), 400

    db = get_db()
    try:
        # Validate questionnaire exists
        q = db.query(Questionnaire).filter_by(id=questionnaire_id).first()
        if not q:
            return jsonify({"error": "Questionnaire not found"}), 404

        # Delete existing answers for this user + questionnaire (upsert)
        db.query(Answer).filter_by(
            user_id=user_id,
            questionnaire_id=questionnaire_id,
        ).delete()

        # Save new answers
        saved = []
        for ans in answers_data:
            answer = Answer(
                id=str(uuid.uuid4()),
                user_id=user_id,
                question_id=ans["question_id"],
                questionnaire_id=questionnaire_id,
                scale_value=ans.get("scale_value"),
                text_value=ans.get("text_value"),
                choice_value=str(ans.get("choice_value")) if ans.get("choice_value") else None,
            )
            db.add(answer)
            saved.append(answer)

        db.commit()

        return jsonify({
            "success": True,
            "count": len(saved),
            "message": f"已保存 {len(saved)} 条回答",
        })
    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()


@questionnaire_bp.route("/answers/me", methods=["GET"])
def get_my_answers():
    """获取当前用户的所有回答。"""
    user_id = request.headers.get("X-User-Id")
    if not user_id:
        return jsonify({"error": "X-User-Id header required"}), 401

    db = get_db()
    try:
        answers = db.query(Answer).filter_by(user_id=user_id).all()
        return jsonify({
            "success": True,
            "answers": [a.to_dict() for a in answers],
        })
    finally:
        db.close()
