from django.contrib import admin

from .models import Goal, Group, Match, Player, Team

class GoalInline(admin.TabularInline):
    model = Goal
    fields = ("scorer", "assister")
    extra = 0


class PlayerInline(admin.TabularInline):
    model = Player
    extra = 0


@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ("scorer", "match")
    list_filter = ("match",)


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    search_fields = ("name",)

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ("name", "team")
    list_filter = ("team",)
    search_fields = ("name", "team__name")
    extra = 0
    show_change_link = True
    verbose_name_plural = "Roster"

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ("name", "group")
    list_filter = ("group",)
    search_fields = ("name", "players__name")
    inlines = (PlayerInline,)


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ("home_team", "away_team", "kickoff", "venue", "final_score")
    ordering = ("kickoff",)

    @admin.display(description="Final score")
    def final_score(self, obj):
        if obj.home_score is None or obj.away_score is None:
            return "Pending"
        return f"{obj.home_score}–{obj.away_score}"

    def get_inlines(self, request, obj=None):
        return (GoalInline,) if obj is not None else ()
    
    def get_fieldsets(self, request, obj=None):
        fixture = (
            "Fixture details",
            {"fields": ("home_team", "away_team", "stage", "kickoff", "venue")},
        )

        if obj is None:
            return (fixture,)

        return (
            fixture,
            (
                "Final result",
                {
                    "fields": ("home_score", "away_score"),
                    "description": "Enter both scores after the final whistle.",
                },
            ),
        )