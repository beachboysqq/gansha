在google-appenegin的文档中看到一篇文章介绍 Google App Engine Helper(http://code.google.com/appengine/articles/appengine_helper_for_django.html)，这是一个模拟在GAE上模拟django环境的开源软件包。svn版本已经开始支持django1.0以上的版本了，支持jango authentication框架和django 测试框架，适合用来在GAE上构建大型的django应用程序。

具体搭建步骤如下：
1.安装GAE和django 1.0.2
2.下载appengine\_helper\_for\_django，并把该目录改名成project目录，删除svn文件
svn co http://google-app-engine-django.googlecode.com/svn/trunk/ \
appengine\_helper\_for\_django
3.为google-appengine建立符号链接
ln -s /home/me/google\_appengine /home/me/myproject/.google\_appengine
4.复制django源文件（django目录）到project 目录下。如下文件可删除
django/bin
django/contrib/admin
django/contrib/databrowse
5.在project目录下，执行python manage.py runserver.如果没错的话，就会出现以下提示：
It worked!
Congratulations on your first Django-powered page.

注意：
（1）使用import from 时，不要包括project目录（,而应从子目录开始。例如，假设你的project目录为mysite，appengine\_django和django目录都在mysite下。
(2)不要从其他project中复制文件，否则还是会引用原来的文件，很奇怪!