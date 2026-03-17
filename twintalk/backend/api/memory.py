"""Memory API — CRUD for key memories (用户主动添加的关键记忆)."""

import uuid
from flask import Blueprint, request, jsonify
from database import get_db
from models.profile import KeyMemory, UserProfile

memory_bp = Blueprint("memory", __name__, url_prefix="/api/memories")


@memory_bp.route("/", methods=["GET"])
def list_memories():
    """获取当前用户的所有关键记忆。"""
    user_id = request.headers.get("X-User-Id")
    if not user_id:
        return jsonify({"error": "X-User-Id header required"}), 401

    db = get_db()
    try:
        memories = (
            db.query(KeyMemory)
            .filter_by(user_id=user_id)
            .order_by(KeyMemory.created_at.desc())
            .all()
        )
        return jsonify({
            "success": True,
            "memories": [m.to_dict() for m in memories],
        })
    finally:
        db.close()


@memory_bp.route("/", methods=["POST"])
def add_memory():
    """添加一条关键记忆。"""
    user_id = request.headers.get("X-User-Id")
    if not user_id:
        return jsonify({"error": "X-User-Id header required"}), 401

    data = request.get_json()
    content = (data or {}).get("content", "").strip()
    if not content:
        return jsonify({"error": "content is required"}), 400

    db = get_db()
    try:
        memory = KeyMemory(
            id=str(uuid.uuid4()),
            user_id=user_id,
            content=content,
            memory_type=data.get("memory_type", "user_added"),
        )
        db.add(memory)

        # Invalidate system prompt cache so next chat includes new memory
        profile = (
            db.query(UserProfile)
            .filter_by(user_id=user_id)
            .order_by(UserProfile.version.desc())
            .first()
        )
        if profile:
            profile.system_prompt_cache = ""

        db.commit()
        return jsonify({
            "success": True,
            "memory": memory.to_dict(),
        }), 201
    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()


@memory_bp.route("/<memory_id>", methods=["DELETE"])
def delete_memory(memory_id):
    """删除一条关键记忆。"""
    user_id = request.headers.get("X-User-Id")
    if not user_id:
        return jsonify({"error": "X-User-Id header required"}), 401

    db = get_db()
    try:
        memory = (
            db.query(KeyMemory)
            .filter_by(id=memory_id, user_id=user_id)
            .first()
        )
        if not memory:
            return jsonify({"error": "Memory not found"}), 404

        db.delete(memory)

        # Invalidate system prompt cache
        profile = (
            db.query(UserProfile)
            .filter_by(user_id=user_id)
            .order_by(UserProfile.version.desc())
            .first()
        )
        if profile:
            profile.system_prompt_cache = ""

        db.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()
