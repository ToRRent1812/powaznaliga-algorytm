using System;
using System.Collections.Generic;

class Player
{
    public string Name;
    public int Points;
    public int MinimumPoints;
    public int Outcome;
    public bool IsPlacement;
    public int PointsAfter;

    public Player(string name, int points, int minPoints, int outcome, bool isPlacement)
    {
        Name = name;
        Points = points;
        MinimumPoints = minPoints;
        Outcome = outcome;
        IsPlacement = isPlacement;
        PointsAfter = points;
    }
}

class MainClass
{
    static readonly string[] RankNames = {"Drewno 1", "Drewno 2", "Drewno 3", "Brąz 1", "Brąz 2", "Brąz 3",
        "Srebro 1", "Srebro 2", "Srebro 3", "Złoto 1", "Złoto 2", "Złoto 3",
        "Platyna 1", "Platyna 2", "Platyna 3", "Szmaragd 1", "Szmaragd 2", "Szmaragd 3",
        "Diament 1", "Diament 2", "Diament 3", "Szafir 1", "Szafir 2", "Szafir 3",
        "Rubin 1", "Rubin 2", "Rubin 3", "Legenda"};
    static readonly int[] RankThresholds = {0,75,150,250,325,400,
        525,625,725,875,1000,1125,
        1300,1450,1600,1800,1975,2150,
        2375,2575,2775,3050,3325,3625,
        3950,4400,5000,999999};
    static readonly double[] Shields = {0.1,0.1,0.1,0.2,0.2,0.2,
        0.3,0.3,0.3,0.4,0.4,0.4,
        0.5,0.5,0.5,0.6,0.6,0.6,
        0.7,0.7,0.7,0.8,0.8,0.8,
        0.9,0.9,0.9,1.0};
    static readonly int[] WorseWin = {50,46,42,39,36,33,31,29,27,26,25};
    static readonly int[] BetterWin = {50,55,60,65,70,75,85,95,105,115,125};
    static readonly int[] BetterLose = {-50,-55,-60,-65,-70,-75,-85,-95,-105,-115,-125};
    static readonly int[] WorseLose = {-50,-45,-40,-35,-30,-25,-22,-19,-16,-13,-10};

    static int GetPlayerRank(int points)
    {
        for (int i = 0; i < RankThresholds.Length; i++)
        {
            if (points < RankThresholds[i])
                return i;
        }
        return RankThresholds.Length - 1;
    }

    static void PrintPlayers(List<Player> players)
    {
        Console.WriteLine("// Baza Graczy //");
        foreach (var player in players)
        {
            int rank = GetPlayerRank(player.Points);
            Console.WriteLine($"{player.Name} | {RankNames[rank - 1]} | {player.Points}pp");
        }
    }

    static void CalculatePoints(List<Player> players, int racers, int multiplier)
    {
        Console.WriteLine("// Obliczenia //");
        for (int i = 0; i < players.Count; i++)
        {
            var player = players[i];
            int myRank = GetPlayerRank(player.Points);

            if (player.Outcome == 0 && !player.IsPlacement)
            {
                if(myRank <= 6)
                    player.PointsAfter = player.Points-1;
                else if(myRank > 6 && myRank <= 12)
                    player.PointsAfter = player.Points-2;
                else if(myRank > 12 && myRank <= 18)
                    player.PointsAfter = player.Points-3;
                else if(myRank > 18 && myRank <= 24)
                    player.PointsAfter = player.Points-4;
                else if(myRank > 24 && myRank <= 28)
                    player.PointsAfter = player.Points-5;
                if(player.PointsAfter < 0)
                    player.PointsAfter = 0;
                if(player.PointsAfter < player.MinimumPoints)
                    player.PointsAfter = player.MinimumPoints;
            }
            else if(player.Outcome == 0 && player.IsPlacement)
                player.PointsAfter = player.Points;
            else
            {
                double change = 0;
                for (int j = 0; j < players.Count; j++)
                {
                    if (player.Outcome < players[j].Outcome && players[j].Outcome != 0)
                    {
                        int hisrank = GetPlayerRank(players[j].Points);
                        int rankdiff = Math.Abs(hisrank-myRank);
                        if(rankdiff >= 10)
                            rankdiff = 10;
                        if(myRank < hisrank)
                        {
                          change += BetterWin[rankdiff];
                          Console.WriteLine(player.Name+" pokonał "+players[j].Name+". "+rankdiff+" lvl różnicy, +"+BetterWin[rankdiff]+"pp");
                        }
                        else if(myRank >= hisrank)
                        {
                          change += WorseWin[rankdiff];
                          Console.WriteLine(player.Name+" pokonał "+players[j].Name+". "+rankdiff+" lvl różnicy, +"+WorseWin[rankdiff]+"pp");
                        }
                    }
                    else if (player.Outcome > players[j].Outcome && players[j].Outcome != 0)
                    {
                        int hisrank = GetPlayerRank(players[j].Points);
                        int rankdiff = Math.Abs(hisrank-myRank);
                        if(rankdiff >= 10)
                            rankdiff = 10;
                        if(myRank < hisrank)
                        {
                          change += WorseLose[rankdiff];
                          Console.WriteLine(player.Name+" przegrał z "+players[j].Name+". "+rankdiff+" lvl różnicy, "+WorseLose[rankdiff]+"pp");
                        }
                        else if(myRank >= hisrank)
                        {
                          change += BetterLose[rankdiff];
                          Console.WriteLine(player.Name+" przegrał z "+players[j].Name+". "+rankdiff+" lvl różnicy, "+BetterLose[rankdiff]+"pp");
                        }
                    }
                }
                change /= racers-1;
                change *= multiplier;
                if(player.IsPlacement)
                    change *= 2;
                if(change < 0 && !player.IsPlacement)
                    change = change*Shields[myRank-1];
                int changeint = Convert.ToInt16(Math.Floor(change));
                player.PointsAfter = player.Points+changeint;
                if(player.PointsAfter < 0)
                    player.PointsAfter = 0;
                if(player.PointsAfter < player.MinimumPoints)
                    player.PointsAfter = player.MinimumPoints;
                if(change > 0) 
                    Console.WriteLine($"{player.Name} zdobył {changeint} pp");
                else if(change < 0)
                    Console.WriteLine($"{player.Name} stracił {changeint} pp");
            }
        } 
    }

    static void PrintResults(List<Player> players)
    {
        Console.WriteLine("");
        Console.WriteLine("// Ranking po wyścigu //");
        foreach (var player in players)
        {
            int rank = GetPlayerRank(player.PointsAfter);
            int needed = RankThresholds[rank] - player.PointsAfter;
            int difference = player.PointsAfter - player.Points;
            string diffStr = difference >= 0 ? $"+{difference}pp" : $"{difference}pp";
            Console.WriteLine($"[{RankNames[rank - 1]}] {player.Name}    {player.PointsAfter}pp ({diffStr}).    Awans za {needed}pp");
        }
    }

    static void Main()
    {
        int racers = 0;
        var players = new List<Player>
        {
            new Player("Frox", 1826, 779, 0, true),
            new Player("Rajzon", 959, 429, 0, true),
            new Player("Rabbit", 1199, 490, 0, false),
            new Player("Pdlk0", 727, 345, 0, true),
            new Player("Osiek", 517, 104, 0, true),
            new Player("Boko", 303, 29, 0, true),
            new Player("Mystus", 132, 42, 0, true),
            new Player("Dedazen", 250, 0, 0, true),
            new Player("Xeon", 484, 65, 0, true),
            new Player("Duke", 795, 184, 0, false),
            new Player("Shiona", 264, 14, 0, true),
            new Player("Indy", 258, 8, 0, true),
            new Player("Alf", 462, 36, 0, true),
            new Player("Gato", 267, 17, 0, true),
        };

        foreach(var player in players)
        {
            if(player.Outcome > 0)
                racers += 1;
        }

        int multiplier = 1; // Globalny mnożnik na mini sezony

        PrintPlayers(players);
        CalculatePoints(players, racers, multiplier);
        PrintResults(players);
    }
}
