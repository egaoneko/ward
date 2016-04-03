# The MIT License (MIT)
#
# Copyright (c) 2015 pjwards.com
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# ==================================================================================
""" Sets models """

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from mezzanine.core.managers import SearchableManager


def get_different_time(time):
    """
    Get different time from input time

    :param time: time for compare
    :return: days or hours or minutes or seconds ago
    """
    now = timezone.now()

    diff = now - time
    s = diff.total_seconds()
    hours, remainder = divmod(s, 3600)
    minutes, seconds = divmod(remainder, 60)

    if diff.days > 0:
        return str(int(diff.days)) + "days"
    elif hours > 0:
        return str(int(hours)) + "hours"
    elif minutes > 0:
        return str(int(minutes)) + "mins"
    else:
        return str(int(seconds)) + "secs"


class Group(models.Model):
    """
    Facebook Group model
    """
    id = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    updated_time = models.DateTimeField()
    privacy = models.CharField(max_length=30)
    is_stored = models.BooleanField(default=False)
    post_count = models.IntegerField(default=0)
    comment_count = models.IntegerField(default=0)
    owner = models.ForeignKey('FBUser', null=True, related_name='group_owner')

    # Enroll field in Mezzanine Search Engine
    objects = SearchableManager()
    search_fields = ("name",)

    def __str__(self):
        return self.id

    def is_updated(self, new_updated_time):
        """
        Check group is updated.

        :param new_updated_time: json datetime
        :return: True is updated and False is not updated
        """
        return self.updated_time.strftime('%Y-%m-%dT%H:%M:%S') != new_updated_time.split('+')[0]

    def get_diff_time(self):
        """
        Get different time from updated time

        :return: different time
        """
        return get_different_time(self.updated_time)

    @staticmethod
    def get_unit(number):
        """
        Get unit number

        :param number: number
        :return: unit number
        """

        if number > 1000:
            return str(int(number / 1000)) + 'K'
        else:
            return number

    def get_post_count_unit(self):
        """
        Get post count unit

        :return: post count unit number
        """
        return Group.get_unit(self.post_count)

    def get_comment_count_unit(self):
        """
        Get comment count unit

        :return: comment count unit number
        """
        return Group.get_unit(self.comment_count)


class FBUser(models.Model):
    """
    Facebook User model
    """
    id = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=50)
    picture = models.CharField(max_length=2083, null=True, blank=True)
    groups = models.ManyToManyField(Group)
    updated_time = models.DateTimeField(auto_now_add=True)

    # Enroll field in Mezzanine Search Engine
    objects = SearchableManager()
    search_fields = ("name",)

    def __str__(self):
        return self.id

    def is_update(self):
        """
        Check update is possible. (per 1 day)

        :return:
        """
        now = timezone.now()
        diff = now - self.updated_time

        if diff.days >= 1:
            return True
        return False


class Post(models.Model):
    """
    Facebook Post model
    """
    id = models.CharField(max_length=50, primary_key=True)
    user = models.ForeignKey(FBUser, related_name='posts')
    created_time = models.DateTimeField()
    updated_time = models.DateTimeField()
    message = models.TextField(null=True, blank=True)
    picture = models.CharField(max_length=2083, null=True, blank=True)
    comment_count = models.IntegerField(default=0)
    like_count = models.IntegerField(default=0)
    share_count = models.IntegerField(default=0)
    group = models.ForeignKey(Group, related_name='posts')
    is_show = models.BooleanField(default=True)

    # Enroll field in Mezzanine Search Engine
    objects = SearchableManager()
    search_fields = ("message",)

    def __str__(self):
        return self.id

    def is_updated(self, new_updated_time):
        """
        Check post is updated.

        :param new_updated_time: json datetime
        :return: True is updated and False is not updated
        """
        return self.updated_time.strftime('%Y-%m-%dT%H:%M:%S') != new_updated_time.split('+')[0]

    def get_diff_cre_time(self):
        """
        Get different time from created time

        :return: different time
        """
        return get_different_time(self.created_time)

    def get_diff_upe_time(self):
        """
        Get different time from updated time

        :return: different time
        """
        return get_different_time(self.updated_time)


class Comment(models.Model):
    """
    Facebook Comment model
    """
    id = models.CharField(max_length=20, primary_key=True)
    user = models.ForeignKey(FBUser, related_name='comments')
    created_time = models.DateTimeField()
    message = models.TextField(null=True, blank=True)
    like_count = models.IntegerField(default=0)
    comment_count = models.IntegerField(default=0)
    post = models.ForeignKey(Post, related_name='comments')
    parent = models.ForeignKey('Comment', null=True, related_name='comments')
    group = models.ForeignKey(Group, related_name='comments')
    is_show = models.BooleanField(default=True)

    # Enroll field in Mezzanine Search Engine
    objects = SearchableManager()
    search_fields = ("message",)

    def __str__(self):
        return self.id

    def get_diff_cre_time(self):
        """
        Get different time from created time

        :return: different time
        """
        return get_different_time(self.created_time)


class Media(models.Model):
    """
    Facebook Media model that is part of Attachment
    """
    height = models.IntegerField(null=True)
    width = models.IntegerField(null=True)
    src = models.CharField(max_length=2083, null=True, blank=True)


class Attachment(models.Model):
    """
    Facebook Attachment model that is part of Post and Comment
    """
    post = models.ForeignKey(Post, null=True, related_name='attachments')
    comment = models.ForeignKey(Comment, null=True, related_name='attachments')
    url = models.CharField(max_length=2083, null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    type = models.CharField(max_length=30, null=True, blank=True)

    # photo, share, unavailable, album(sub), video_autoplay, multi_share(sub), video_share_youtube, note
    media = models.ForeignKey(Media, null=True, related_name='media')

    objects = SearchableManager()
    search_fields = ("description",)


class Blacklist(models.Model):
    """
    Blacklist model for facebook user who wrote spams
    """
    group = models.ForeignKey(Group, related_name='blacklist')
    user = models.ForeignKey(FBUser, related_name='blacklist')
    count = models.IntegerField(default=0)
    updated_time = models.DateTimeField(auto_now=True)


class Report(models.Model):
    """
    Report model about spams
    """
    post = models.ForeignKey(Post, null=True, related_name='reports')
    comment = models.ForeignKey(Comment, null=True, related_name='reports')
    group = models.ForeignKey(Group, related_name='reports')
    user = models.ForeignKey(FBUser, related_name='reports')
    status = models.CharField(max_length=30, default='new')
    updated_time = models.DateTimeField(auto_now=True)


class DeletedPost(models.Model):
    """
    Deleted Post model for post deleted by group owner or super user
    """
    id = models.CharField(max_length=50, primary_key=True)
    user = models.ForeignKey(FBUser, related_name='delete_posts')
    created_time = models.DateTimeField()
    updated_time = models.DateTimeField()
    message = models.TextField(null=True, blank=True)
    picture = models.CharField(max_length=2083, null=True, blank=True)
    comment_count = models.IntegerField(default=0)
    like_count = models.IntegerField(default=0)
    share_count = models.IntegerField(default=0)
    group = models.ForeignKey(Group, related_name='delete_posts')

    # Enroll field in Mezzanine Search Engine
    objects = SearchableManager()
    search_fields = ("message",)

    def __str__(self):
        return self.id

    def is_updated(self, new_updated_time):
        """
        Check post is updated.

        :param new_updated_time: json datetime
        :return: True is updated and False is not updated
        """
        return self.updated_time.strftime('%Y-%m-%dT%H:%M:%S') != new_updated_time.split('+')[0]

    def get_diff_cre_time(self):
        """
        Get different time from created time

        :return: different time
        """
        return get_different_time(self.created_time)

    def get_diff_upe_time(self):
        """
        Get different time from updated time

        :return: different time
        """
        return get_different_time(self.updated_time)

    @classmethod
    def create(cls, post):
        return cls(id=post.id, user=post.user, created_time=post.created_time, updated_time=post.updated_time,
                   message=post.message, picture=post.picture, comment_count=post.comment_count,
                   like_count=post.like_count, share_count=post.share_count, group=post.group)


class DeletedComment(models.Model):
    """
    Deleted Comment model for comment deleted by group owner or super user
    """
    id = models.CharField(max_length=20, primary_key=True)
    user = models.ForeignKey(FBUser, related_name='delete_comments')
    created_time = models.DateTimeField()
    message = models.TextField(null=True, blank=True)
    like_count = models.IntegerField(default=0)
    comment_count = models.IntegerField(default=0)
    post = models.CharField(max_length=50)
    parent = models.CharField(max_length=20, null=True)
    group = models.ForeignKey(Group, related_name='delete_comments')

    # Enroll field in Mezzanine Search Engine
    objects = SearchableManager()
    search_fields = ("message",)

    def __str__(self):
        return self.id

    def get_diff_cre_time(self):
        """
        Get different time from created time

        :return: different time
        """
        return get_different_time(self.created_time)

    @classmethod
    def create(cls, comment):
        if comment.parent:
            parent = comment.parent.id
        else:
            parent = None
        return cls(id=comment.id, user=comment.user, created_time=comment.created_time, message=comment.message,
                   like_count=comment.like_count, comment_count=comment.comment_count, post=comment.post.id,
                   parent=parent, group=comment.group)


class Ward(models.Model):
    """
    Ward model for ward that is a post or comment saved by user for watching
    """
    user = models.ForeignKey(User, related_name='wards')
    group = models.ForeignKey(Group, related_name='wards')
    post = models.ForeignKey(Post, null=True, related_name='wards')
    comment = models.ForeignKey(Comment, null=True, related_name='wards')
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now_add=True)

    def is_updated(self, new_updated_time):
        """
        Check post is updated.

        :param new_updated_time: json datetime
        :return: True is updated and False is not updated
        """
        return self.updated_time.strftime('%Y-%m-%dT%H:%M:%S') != new_updated_time.split('+')[0]


class UserActivity(models.Model):
    """
    Table about user activity for performance
    """
    user = models.ForeignKey(FBUser, related_name='user_activities')
    group = models.ForeignKey(Group, related_name='user_activities')
    post_count = models.IntegerField(default=0)
    comment_count = models.IntegerField(default=0)

    @classmethod
    def add_post_count(cls, user, group):
        """
        Add post count

        :param user: user
        :param group: group
        :return:
        """
        if not UserActivity.objects.filter(user=user, group=group).exists():
            user_activity = UserActivity(user=user, group=group, post_count=1)
            user_activity.save()
        else:
            user_activity = UserActivity.objects.filter(user=user, group=group)[0]
            user_activity.post_count += 1
            user_activity.save()

    @classmethod
    def add_comment_count(cls, user, group):
        """
        Add comment count

        :param user: user
        :param group: group
        :return:
        """
        if not UserActivity.objects.filter(user=user, group=group).exists():
            user_activity = UserActivity(user=user, group=group, comment_count=1)
            user_activity.save()
        else:
            user_activity = UserActivity.objects.filter(user=user, group=group)[0]
            user_activity.comment_count += 1
            user_activity.save()

    @classmethod
    def sub_post_count(cls, user, group):
        """
        Subtract post count

        :param user: user
        :param group: group
        :return:
        """
        if not UserActivity.objects.filter(user=user, group=group).exists():
            user_activity = UserActivity(user=user, group=group)
            user_activity.save()
        else:
            user_activity = UserActivity.objects.filter(user=user, group=group)[0]
            if user_activity.post_count > 0:
                user_activity.post_count -= 1
            else:
                user_activity.post_count = 0
            user_activity.save()

    @classmethod
    def sub_comment_count(cls, user, group):
        """
        Subtract comment count

        :param user: user
        :param group: group
        :return:
        """
        if not UserActivity.objects.filter(user=user, group=group).exists():
            user_activity = UserActivity(user=user, group=group)
            user_activity.save()
        else:
            user_activity = UserActivity.objects.filter(user=user, group=group)[0]
            if user_activity.comment_count > 0:
                user_activity.comment_count -= 1
            else:
                user_activity.comment_count = 0
            user_activity.save()


class GroupStoreList(models.Model):
    """
    Group store list to check group is store,
    """
    group = models.OneToOneField(Group)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    query = models.CharField(max_length=2083, null=True, blank=True)
    status = models.CharField(max_length=30, default='new')


class InterestGroupList(models.Model):
    """
    Interest group list for easy to check interested group
    """
    user = models.ForeignKey(User, related_name='interest_group_list')
    group = models.ForeignKey(Group, related_name='interest_group_list')


class GroupStatisticsUpdateList(models.Model):
    """
    Group statistics update list for check statistics is update
    """
    group = models.ForeignKey(Group)
    method = models.CharField(max_length=30)
    updated_time = models.DateTimeField(auto_now_add=True)

    @classmethod
    def update(cls, group, method):
        """
        Update list

        :param group: group
        :param method: method
        :return:
        """
        oj = GroupStatisticsUpdateList.objects.filter(group=group, method=method)
        if oj:
            oj[0].updated_time = timezone.now()
            oj[0].save()
        else:
            oj = GroupStatisticsUpdateList(group=group, method=method)
            oj.save()

    def is_update(self):
        """
        Check update is possible. (per 1 day)

        :return:
        """
        now = timezone.now()
        diff = now - self.updated_time

        if diff.days >= 1:
            return True
        return False


class YearGroupStatistics(models.Model):
    """
    Memoization about year group statistics
    """
    group = models.ForeignKey(Group)
    time = models.DateTimeField()
    model = models.CharField(max_length=10)
    count = models.IntegerField(default=0)


class MonthGroupStatistics(models.Model):
    """
    Memoization about month group statistics
    """
    group = models.ForeignKey(Group)
    time = models.DateTimeField()
    model = models.CharField(max_length=10)
    count = models.IntegerField(default=0)


class DayGroupStatistics(models.Model):
    """
    Memoization about day group statistics
    """
    group = models.ForeignKey(Group)
    time = models.DateTimeField()
    model = models.CharField(max_length=10)
    count = models.IntegerField(default=0)


class TimeOverviewGroupStatistics(models.Model):
    """
    Memoization about time overview group statistics
    """
    group = models.ForeignKey(Group)
    time = models.IntegerField(default=0)
    model = models.CharField(max_length=10)
    count = models.IntegerField(default=0)


class GroupArchiveErrorList(models.Model):
    """
    Group archive error list
    """
    group = models.OneToOneField(Group)
    error_count = models.IntegerField(default=1)
    query = models.CharField(max_length=2083, null=True, blank=True)
    message = models.TextField(null=True, blank=True)


class MonthPost(models.Model):
    """
    Memoization about month post
    """
    created_time = models.DateTimeField()
    group = models.ForeignKey(Group)
    post = models.OneToOneField(Post)

    @classmethod
    def create(cls, post):
        """
        Create month post

        :param post: post
        :return:
        """
        # now = timezone.now()
        # diff = now - post.created_time
        # if diff.days > 30:
        #     return

        check(post.group)
        if MonthPost.objects.filter(post=post).exists():
            return

        cls(created_time=post.created_time, group=post.group, post=post).save()

    def is_overtime(self):
        """
        Is this object overtime?

        :return:
        """
        now = timezone.now()
        diff = now - self.created_time

        if diff.days > 30:
            return True
        return False


class MonthComment(models.Model):
    """
    Memoization about month comment
    """
    created_time = models.DateTimeField()
    group = models.ForeignKey(Group)
    comment = models.OneToOneField(Comment)

    @classmethod
    def create(cls, comment):
        """
        Create month comment

        :param comment: comment
        :return:
        """
        # now = timezone.now()
        # diff = now - comment.created_time
        # if diff.days > 30:
        #     return

        check(comment.group)
        if MonthComment.objects.filter(comment=comment).exists():
            return

        cls(created_time=comment.created_time, group=comment.group, comment=comment).save()

    def is_overtime(self):
        """
        Is this object overtime?

        :return:
        """
        now = timezone.now()
        diff = now - self.created_time

        if diff.days > 30:
            return True
        return False


def check(group):
    """
    Check month post and comment, and remove something over 1 month

    :param group: group
    :return:
    """
    # Is ready to update?
    update_list = GroupStatisticsUpdateList.objects.filter(group=group, method='month_content')
    if update_list:
        is_update = update_list[0].is_update()
    else:
        GroupStatisticsUpdateList.update(group=group, method='month_content')
        is_update = False

    if is_update:
        date = timezone.now() - timezone.timedelta(30)
        for oj in MonthPost.objects.filter(group=group, created_time__lt=date):
            oj.delete()

        for oj in MonthComment.objects.filter(group=group, created_time__lt=date):
            oj.delete()
        GroupStatisticsUpdateList.update(group=group, method='month_content')

