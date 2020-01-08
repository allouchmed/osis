from django.contrib import admin

from learning_unit.models import faculty_manager, faculty_manager_learning_unit

admin.site.register(faculty_manager.FacultyManager, faculty_manager.FacultyManagerAdmin)
admin.site.register(
    faculty_manager_learning_unit.FacultyManagerLearningUnit,
    faculty_manager_learning_unit.FacultyManagerLearningUnitAdmin
)
