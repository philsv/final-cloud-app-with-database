from django.contrib import admin

from .models import Choice, Course, Instructor, Learner, Lesson, Question


class LessonInline(admin.StackedInline):
    model = Lesson
    extra = 5


class QuestionInline(admin.StackedInline):
    model = Question


class ChoiceInline(admin.StackedInline):
    model = Choice


class CourseAdmin(admin.ModelAdmin):
    inlines = [LessonInline]
    list_display = ('name', 'pub_date')
    list_filter = ['pub_date']
    search_fields = ['name', 'description']


class LessonAdmin(admin.ModelAdmin):
    list_display = ['title']


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'get_course_name', 'question_grade')

    def get_course_name(self, obj):
        return obj.lesson.course.name if obj.lesson else ''
    get_course_name.short_description = 'Course'  # type: ignore


class ChoiceAdmin(admin.ModelAdmin):
    list_display = ['choice_text', 'question']


admin.site.register(Question, QuestionAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Choice, ChoiceAdmin)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(Instructor)
admin.site.register(Learner)
