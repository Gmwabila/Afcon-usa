from django.db import models
from django.shortcuts import get_object_or_404, render

from .models import Goal ,Group, Match, Team


def standings(request):
    groups = Group.objects.order_by("name").prefetch_related("teams")
    tables = []
    rows_by_team = {}

    for group in groups:
        rows = []
        for team in group.teams.all():
            row = {
                "team": team.name,
                "played": 0,
                "wins": 0,
                "draws": 0,
                "losses": 0,
                "gf": 0,
                "ga": 0,
                "gd": 0,
                "points": 0,
            }
            rows.append(row)
            rows_by_team[team.pk] = row

        tables.append({"name": group.name, "rows": rows})

    matches = Match.objects.filter(
        stage=Match.Stage.GROUP,
        home_score__isnull=False,
        away_score__isnull=False,
        home_team__group__isnull=False,
        home_team__group_id=models.F("away_team__group_id"),
    )

    for match in matches:
        home = rows_by_team[match.home_team_id]
        away = rows_by_team[match.away_team_id]

        for row, scored, conceded in (
            (home, match.home_score, match.away_score),
            (away, match.away_score, match.home_score),
        ):
            row["played"] += 1
            row["gf"] += scored
            row["ga"] += conceded
            row["gd"] += scored - conceded

            if scored > conceded:
                row["wins"] += 1
                row["points"] += 3
            elif scored == conceded:
                row["draws"] += 1
                row["points"] += 1
            else:
                row["losses"] += 1

    for table in tables:
        table["rows"].sort(
            key=lambda row: (
                -row["points"],
                -row["gd"],
                -row["gf"],
                row["team"].casefold(),
            )
        )

    return render(request, "tournament/standings.html", {"tables": tables})
def match_lists(matches):
    matches = matches.select_related("home_team", "away_team")

    return {
        "upcoming": matches.filter(
            home_score__isnull=True,
            away_score__isnull=True,
        ).order_by("kickoff", "pk"),
        "results": matches.filter(
            home_score__isnull=False,
            away_score__isnull=False,
        ).order_by("-kickoff", "-pk"),
    }


def fixtures(request):
    return render(
        request,
        "tournament/fixtures.html",
        match_lists(Match.objects.all()),
    )


def teams(request):
    return render(
        request,
        "tournament/teams.html",
        {"teams": Team.objects.select_related("group").order_by("name")},
    )


def team_detail(request, pk):
    team = get_object_or_404(Team.objects.select_related("group"), pk=pk)
    matches = Match.objects.filter(
        models.Q(home_team=team) | models.Q(away_team=team)
    )
    context = match_lists(matches)
    context["team"] = team
    context["players"] = team.players.order_by("name", "pk")

    return render(request, "tournament/team_detail.html", context)
def player_stats(request):
    goals = Goal.objects.filter(
        match__home_score__isnull=False,
        match__away_score__isnull=False,
    )

    top_scorers = (
        goals.values(
            player_id=models.F("scorer_id"),
            player_name=models.F("scorer__name"),
            team_name=models.F("scorer__team__name"),
        )
        .annotate(total=models.Count("pk"))
        .order_by("-total", "player_name", "team_name", "player_id")
    )

    top_assists = (
        goals.filter(assister__isnull=False)
        .values(
            player_id=models.F("assister_id"),
            player_name=models.F("assister__name"),
            team_name=models.F("assister__team__name"),
        )
        .annotate(total=models.Count("pk"))
        .order_by("-total", "player_name", "team_name", "player_id")
    )

    return render(
        request,
        "tournament/player_stats.html",
        {
            "leaderboards": [
                {"title": "Top Scorers", "label": "Goals", "rows": top_scorers},
                {"title": "Top Assists", "label": "Assists", "rows": top_assists},
            ]
        },
    )
def match_detail(request, pk):
    match = get_object_or_404(
        Match.objects.select_related("home_team", "away_team"),
        pk=pk,
    )
    is_final = match.home_score is not None and match.away_score is not None

    return render(
        request,
        "tournament/match_detail.html",
        {
            "match": match,
            "is_final": is_final,
            "goals": (
                match.goals.select_related("scorer__team", "assister").order_by("pk")
                if is_final
                else Match._meta.get_field("goals").related_model.objects.none()
            ),
        },
    )
def home(request):
    matches = match_lists(Match.objects.all())

    return render(
        request,
        "tournament/home.html",
        {
            "upcoming": matches["upcoming"][:3],
            "results": matches["results"][:3],
        },
    )