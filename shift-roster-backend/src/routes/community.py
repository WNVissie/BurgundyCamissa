from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from src.models.models import db, CommunityPost, PostReply, User
from src.utils.decorators import get_current_user, manager_required

community_bp = Blueprint('community', __name__)

@community_bp.route('/posts', methods=['GET'])
@jwt_required()
def get_posts():
    """Get all community posts, newest first."""
    try:
        posts = CommunityPost.query.order_by(CommunityPost.created_at.desc()).all()
        return jsonify([post.to_dict() for post in posts]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@community_bp.route('/posts', methods=['POST'])
@jwt_required()
def create_post():
    """Create a new community post."""
    try:
        current_user = get_current_user()
        data = request.get_json()

        title = data.get('title')
        content = data.get('content')
        post_type = data.get('post_type', 'Question')

        if not title or not content:
            return jsonify({'error': 'Title and content are required'}), 400

        # Only admins/managers can create announcements
        if post_type == 'Announcement' and current_user.role_ref.name not in ['Admin', 'Manager']:
            return jsonify({'error': 'You do not have permission to create announcements'}), 403

        new_post = CommunityPost(
            user_id=current_user.id,
            title=title,
            content=content,
            post_type=post_type
        )
        db.session.add(new_post)
        db.session.commit()

        return jsonify(new_post.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@community_bp.route('/posts/<int:post_id>', methods=['GET'])
@jwt_required()
def get_post_details(post_id):
    """Get a single post and its replies."""
    try:
        post = CommunityPost.query.get(post_id)
        if not post:
            return jsonify({'error': 'Post not found'}), 404

        replies = PostReply.query.filter_by(post_id=post_id).order_by(PostReply.created_at.asc()).all()

        post_data = post.to_dict()
        post_data['replies'] = [reply.to_dict() for reply in replies]

        return jsonify(post_data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@community_bp.route('/posts/<int:post_id>/reply', methods=['POST'])
@jwt_required()
def add_reply(post_id):
    """Add a reply to a post."""
    try:
        current_user = get_current_user()
        data = request.get_json()
        content = data.get('content')

        if not content:
            return jsonify({'error': 'Reply content cannot be empty'}), 400

        post = CommunityPost.query.get(post_id)
        if not post:
            return jsonify({'error': 'Post not found'}), 404

        new_reply = PostReply(
            user_id=current_user.id,
            post_id=post_id,
            content=content
        )
        db.session.add(new_reply)
        db.session.commit()

        return jsonify(new_reply.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@community_bp.route('/posts/<int:post_id>', methods=['DELETE'])
@jwt_required()
def delete_post(post_id):
    """Delete a post."""
    try:
        current_user = get_current_user()
        post = CommunityPost.query.get(post_id)
        if not post:
            return jsonify({'error': 'Post not found'}), 404

        # Check permissions: must be author or admin/manager
        if post.user_id != current_user.id and current_user.role_ref.name not in ['Admin', 'Manager']:
            return jsonify({'error': 'You do not have permission to delete this post'}), 403

        db.session.delete(post)
        db.session.commit()

        return jsonify({'message': 'Post deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
