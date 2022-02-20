from flask import Blueprint, request

from flask_restful import Api, Resource
from sqlalchemy.orm import query
from .Models.post_model import PostSchema, PostModel
from .Models.like_model import LikeModel
from .Models.comment_model import CommentModel, CommentSchema
from flask_jwt_extended import jwt_required, get_jwt, verify_jwt_in_request, get_jwt_identity
from werkzeug.routing import ValidationError

post = Blueprint('post', __name__, url_prefix='/post')
api = Api(post)

post_schema = PostSchema()
comment_schema = CommentSchema()

class Post(Resource):
    def get(self, pid):
        try:
            user = Post.get_identity_if_loggedin()
            if user:
                caller_id = get_jwt_identity()
                like_check = LikeModel.check_like(pid=pid, uid=caller_id)
                post = PostModel.get_post_by_id(pid)
                return {
                    'pid': post.pid,
                    'title': post.title,
                    'body': post.body,
                    'author': PostModel.get_post_author(post.author_id),
                    'pub_date': str(post.pub_date),
                    'like': like_check
                }, 200
            else:
                post = PostModel.get_post_by_id(pid)
                return {
                    'pid': post.pid,
                    'title': post.title,
                    'body': post.body,
                    'author': PostModel.get_post_author(post.author_id),
                    'pub_date': str(post.pub_date),
                    'like': False
                }, 200
        except Exception as e:
            print(e)
            return {
                'pid': -1,
                'title': '',
                'body': '',
                'pub_date': '',
                'like': False
            }, 500
    
    @jwt_required()
    def delete(self, pid):
        try:
            caller_id = get_jwt()['uid']
            post_to_del = PostModel.get_post_by_id(pid)
            if caller_id == post_to_del.author_id: # ownership check
                post_to_del.delete_post()
                return {'msg': 'Post deleted'}, 200
            else:
                return {'msg': 'You are not the owner of this post.'}, 400
            
        except Exception as e:
            return {'msg': 'Server error.'}, 500

    @staticmethod
    def get_identity_if_loggedin():
        try:
            verify_jwt_in_request(optional=True)
            return get_jwt_identity()
        except Exception:
            pass
            
class PostCreate(Resource):
    @jwt_required()
    def post(self):
        try:
            post_data = post_schema.load(request.json)
            print(post_data)
            print(get_jwt())
            author_id = get_jwt_identity()
            print(author_id)
            post_data['author_id'] = author_id # append uid got from jwt token
            #print(post_data)
            new_post = PostModel(post_data)
            #print(new_post)
            new_post.save_db()

            return {'msg': 'post created'}, 200

        except ValidationError as error:
            print(error)
            return {'msg': 'error'}, 400

        except Exception as e:
            print(e)
            print(e)
            return {'msg': 'Server error.'}, 500

class PostList(Resource):
    def get(self):
        try:
            posts = PostModel.get_all_post()
            posts_list = []
            if len(posts) == 0:
                return [], 200
            else:
                for post in posts:
                    posts_list.append({
                        'pid': post.pid,
                        'title': post.title,
                        'author': PostModel.get_post_author(post.author_id),
                        'pub_date': str(post.pub_date),
                        'tag': post.tag
                    })
                return posts_list, 200
        except Exception as e:
            return [], 500

class LikePost(Resource):
    @jwt_required()
    def post(self, pid):
        try:
            caller_id = get_jwt_identity()
            like_data = {'post_id':pid, 'user_id':caller_id}
            like = LikeModel(like_data)
            like.save_db()
            return {'msg': 'Post liked.'}, 200
            
        except Exception as e:
            print(e)
            return {'msg': 'Server error.'}, 500

    @jwt_required()
    def delete(self, pid):
        try:
            caller_id = get_jwt_identity()
            post_to_dislike = LikeModel.get_like_by_ids(pid, caller_id)
            if post_to_dislike != None:
                post_to_dislike.delete_like()
                return {'msg': 'Unliked post.'}, 200
            else:
                return {'msg': 'Post has not been liked before.'}, 400
            
        except Exception as e:
            return {'msg': 'Server error.'}, 500

class CommentPost(Resource):
    def get(self, pid):
        try:
            comments = CommentModel.get_all_comment_post_id(pid)
            # print(comments)
            comments_list = []
            if len(comments) == 0:
                return comments_list, 200
            else:
                for comment in comments:
                    # print(comment)
                    comments_list.append({
                        'cid': comment.cid,
                        'body': comment.body,
                        'author': CommentModel.get_comment_author(comment.author_id),
                        'pub_date': str(comment.pub_date)
                    })
                return comments_list, 200
        except Exception as e:
            print(e)
            return [], 500

    @jwt_required()
    def post(self, pid):
        try:
            comment_data = comment_schema.load(request.json)
            comment_data['post_id'] = pid
            author_id = get_jwt_identity()
            comment_data['author_id'] = author_id
            new_comment = CommentModel(comment_data)
            new_comment.save_db()

            return {'msg': 'Comment posted.'}, 200

        except Exception as e:
            print(e)
            return {'msg': 'Server error.'}, 500

class Tag(Resource):
    def get(self, tag):
        try:
            # print(tag)
            posts = PostModel.get_posts_by_tag(tag)
            # print(posts)
            posts_list = []
            if len(posts) == 0:
                return [], 200
            else:
                for post in posts:
                    posts_list.append({
                        'pid': post.pid,
                        'title': post.title,
                        'author': PostModel.get_post_author(post.author_id),
                        'pub_date': str(post.pub_date),
                        'tag': post.tag
                    })
                return posts_list, 200

        except Exception as e:
            print(e)
            return [], 500

api.add_resource(PostCreate, '/create')
api.add_resource(Post, '/<pid>')
api.add_resource(PostList, '/')
api.add_resource(LikePost, '/<pid>/like-dislike')
api.add_resource(CommentPost, '/<pid>/comment')
api.add_resource(Tag, '/tag/<tag>')
