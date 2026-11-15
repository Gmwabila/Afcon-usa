from django.core.exceptions import ValidationError
from django.db import models

class Group(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name
    
class Team(models.Model):
    name = models.CharField(max_length=100, unique=True)
    group = models.ForeignKey(
        Group,
        on_delete=models.PROTECT,
        related_name="teams",
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.name


class Player(models.Model):
    team = models.ForeignKey(
        Team, on_delete=models.PROTECT, related_name="players"
    )
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} ({self.team})"

class Match(models.Model):
    home_team = models.ForeignKey(
        Team, on_delete=models.PROTECT, related_name="home_matches"
    )
    away_team = models.ForeignKey(
        Team, on_delete=models.PROTECT, related_name="away_matches"
    )
    kickoff = models.DateTimeField()
    venue = models.CharField(max_length=120)
    home_score = models.PositiveSmallIntegerField(null=True, blank=True)
    away_score = models.PositiveSmallIntegerField(null=True, blank=True)

    class Stage(models.TextChoices):
        GROUP = "group", "Group stage"
        KNOCKOUT = "knockout", "Knockout stage"

    stage = models.CharField(max_length=10, choices=Stage.choices, blank=True)

    def clean(self):
        super().clean()

        if self.stage == self.Stage.GROUP and self.home_team_id and self.away_team_id:
            home_group = self.home_team.group_id
            away_group = self.away_team.group_id

            if home_group is None or home_group != away_group:
                raise ValidationError(
                    "Both teams must belong to the same group for a group-stage match."
                )

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=~models.Q(home_team=models.F("away_team")),
                name="match_teams_must_differ",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(home_score__isnull=True, away_score__isnull=True)
                    | models.Q(home_score__isnull=False, away_score__isnull=False)
                ),
                name="match_scores_entered_together",
            ),
        ]

    def __str__(self):
        return f"{self.home_team} vs {self.away_team}"


class Goal(models.Model):
    match = models.ForeignKey(
        Match, on_delete=models.CASCADE, related_name="goals"
    )
    scorer = models.ForeignKey(
        Player, on_delete=models.PROTECT, related_name="goals_scored"
    )
    assister = models.ForeignKey(
        Player,
        on_delete=models.PROTECT,
        related_name="goals_assisted",
        null=True,
        blank=True,
    )

    def clean(self):
        super().clean()

        if not self.match_id or not self.scorer_id:
            return

        match_teams = (self.match.home_team_id, self.match.away_team_id)
        if self.scorer.team_id not in match_teams:
            raise ValidationError({
                "scorer": "Choose a player from one of the teams in this match."
            })

        if self.assister_id:
            if self.assister_id == self.scorer_id:
                raise ValidationError({
                    "assister": "Choose a different player for the assist."
                })

            if self.assister.team_id != self.scorer.team_id:
                raise ValidationError({
                    "assister": "Choose a teammate of the scorer."
                })

    def __str__(self):
        return f"{self.scorer} — {self.match}"