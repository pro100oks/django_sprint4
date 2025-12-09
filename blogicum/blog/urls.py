from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('',
         views.PostListView.as_view(),
         name='index'
         ),
    path(
        "edit-profile/",
        views.UserProfileEditView.as_view(),
        name="edit_profile"
    ),
    path(
        "profile/<str:username>/",
        views.UserProfileDetailView.as_view(),
        name="profile"
    ),
    path(
        "posts/create/",
        views.CreatePostView.as_view(),
        name="create_post"
    ),
    path(
        "posts/<int:post_id>/",
        views.PostDetailView.as_view(),
        name="post_detail"
    ),
    path(
        "posts/<int:post_id>/edit/",
        views.EditPostView.as_view(),
        name="edit_post"
    ),
    path(
        "posts/<int:post_id>/delete/",
        views.PostDeleteView.as_view(),
        name="delete_post"
    ),
    path(
        'category/<slug:category_slug>/',
        views.CategoryDetailView.as_view(),
        name='category_posts'
    ),
    path(
        'posts/<int:post_id>/comment/',
        views.AddCommentView.as_view(),
        name='add_comment'
    ),
    path(
        'posts/<int:post_id>/edit_comment/<int:comment_id>/',
        views.EditCommentView.as_view(),
        name='edit_comment'
    ),
    path(
        'posts/<int:post_id>/delete_comment/<int:comment_id>/',
        views.DeleteCommentView.as_view(),
        name='delete_comment'
    )
]
