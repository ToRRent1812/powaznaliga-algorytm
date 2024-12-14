https://www.onlinegdb.com/online_csharp_compiler

using System;

class MainClass 
{
  static int GetPlayerRank (int[] PP, int points) 
  {
    int c;
    for(c=0; c<50; c++)
    {
      if(points < PP[c])
      {
        return c;
      }
    }
    return c;
  }

  static void Main () 
  {
    int[] PP = {0,100,200,300,400,500,600,700,800,900,1050,1200,1350,1500,1650,1800,1950,2100,2250,2400,2600,2800,3000,3200,3400,3700,4000,4300,4600,4900,5300,5700,6100,6500,6900,7400,7900,8400,8900,9400,10000,10600,11200,11800,12400,13100,13900,14800,15800,17000,999999999};
    int[] worse_win = {100,92,85,79,74,70,66,63,60,58,56,54,53,52,51,50};
    int[] better_win = {100,110,120,130,140,150,155,160,165,170,175,180,185,190,195,200};
    int[] better_lose = {-100,-110,-120,-130,-140,-150,-155,-160,-165,-170,-175,-180,-185,-190,-195,-200};
    int[] worse_lose = {-100,-90,-80,-71,-62,-54,-46,-39,-32,-26,-20,-15,-11,-8,-6,-5};

    string[] players = {"Frox", "Rajzon", "Rabbit", "Pdlk0", "Osiek", "Boko", "Mystus", "Dedazen", "Xeon", "SneakiestDuke", "Shionavariel", "IndyCheck"};
    //ID graczy w kolejności pozycji wyścigu
    int[] outcome = {     0,        0,        0,        0,      0,      0,      0,         0,        0,          0,              0,           0};
    int racers = 5; //Ilu graczy uczestniczyło w wyścigu
    int multiplier = 1; // Mnożnik kalkulacji
    int[] pp_before =  
    {
      2322, //0=frox
      1506, //1=rajzon
      1413, //2=Rabbit
      934, //3=pdlk0
      547, //4=osiek
      118, //5=boko
      30, //6=Mystus
      0, //7=Dedazen
      479, //8=Xeon
      1040,  //9=SneakiestDuke
      14, //10=Shionavariel
      8 //11=IndyCheck
    };
    int[] pp_minimum =  
    {
      598, //0=frox
      368, //1=rajzon
      385, //2=Rabbit
      275, //3=pdlk0
      104, //4=osiek
      29, //5=boko
      28, //6=Mystus
      0, //7=Dedazen
      65, //8=Xeon
      133, //9=SneakiestDuke
      14, //10=Shionavariel
      8 //11=IndyCheck
    };
    int[] pp_after = new int[players.Length];

    
    //Pokaz liste graczy, ich power level i PP
		Console.WriteLine("// Baza Graczy //");
    for(int i=0; i<players.Length; i++)
    {
      int rank = GetPlayerRank(PP, pp_before[i]);
      int needed = PP[rank] - pp_before[i];
      Console.WriteLine(players[i]+" | Rank "+rank+" | "+pp_before[i]+"pp | Do Awansu: "+needed+"pp");
    }
    Console.WriteLine("// Obliczenia //");
    for(int i=0; i<pp_before.Length; i++)
    {
      int myrank = GetPlayerRank(PP, pp_before[i]);
      // Jeżeli gracz nie uczestniczył
      if(outcome[i] == 0)
      {
        if(myrank <= 10)
        {
          pp_after[i] = pp_before[i]-1;
        }
        else if(myrank > 10 || myrank <= 20)
        {
          pp_after[i] = pp_before[i]-2;
        }
        else if(myrank > 20 || myrank <= 30)
        {
          pp_after[i] = pp_before[i]-3;
        }
        else if(myrank > 30 || myrank <= 40)
        {
          pp_after[i] = pp_before[i]-4;
        }
        else if(myrank > 40 || myrank <= 50)
        {
          pp_after[i] = pp_before[i]-5;
        }
        // Jeżeli gracz spadł poniżej 0, wyzeruj konto
        if(pp_after[i] < 0)
        {
          pp_after[i] = 0;
        }
        // Jeżeli gracz spadł poniżej minimum, ustaw minimum.
        if(pp_after[i] < pp_minimum[i])
        {
          pp_after[i] = pp_minimum[i];
        }
      }
      else
      {
        double change = 0;
        for(int j=0; j<outcome.Length; j++)
        {
          //Jeżeli gracz zajął lepszą pozycję niż konkurent
          if(outcome[i] < outcome[j] && outcome[j] != 0)
          {
            int hisrank = GetPlayerRank(PP, pp_before[j]);
            int rankdiff = Math.Abs(hisrank-myrank);
            if(rankdiff >= 15)
            {
              rankdiff = 15;
            }
            //Jeżeli gracz ma mniejszą rangę niż konkurent, użyj better_win[]
            if(myrank < hisrank)
            {
              change += better_win[rankdiff];
              Console.WriteLine(players[i]+" pokonał "+players[j]+". "+rankdiff+" lvl różnicy, +"+better_win[rankdiff]+"pp");
            }
            //Jeżeli gracz ma większą rangę niż konkurent, użyj worse_win[]
            else if(myrank >= hisrank)
            {
              change += worse_win[rankdiff];
              Console.WriteLine(players[i]+" pokonał "+players[j]+". "+rankdiff+" lvl różnicy, +"+worse_win[rankdiff]+"pp");
            }
          }
          //Jeżeli gracz zajął gorszą pozycję niż konkurent
          else if(outcome[i] > outcome[j] && outcome[j] != 0)
          {
            int hisrank = GetPlayerRank(PP, pp_before[j]);
            int rankdiff = Math.Abs(hisrank-myrank);
            if(rankdiff >= 15)
            {
              rankdiff = 15;
            }
            //Jeżeli gracz ma mniejszą rangę niż konkurent, użyj worse_lose[]
            if(myrank < hisrank)
            {
              change += worse_lose[rankdiff];
              Console.WriteLine(players[i]+" przegrał z "+players[j]+". "+rankdiff+" lvl różnicy, "+worse_lose[rankdiff]+"pp");
            }
            //Jeżeli gracz ma większą rangę niż konkurent, użyj better_lose[]
            else if(myrank >= hisrank)
            {
              change += better_lose[rankdiff];
              Console.WriteLine(players[i]+" przegrał z "+players[j]+". "+rankdiff+" lvl różnicy, "+better_lose[rankdiff]+"pp");
            }
          }
        }
        //Podziel zdobyte punkty przez ilość przeciwników w wyścigu
        change /= racers-1; //odejmij siebie samego bo potrzebujemy przeciwników
        change *= multiplier; //Pomnóż wynik przez współczynnik
        //Sprawdzanie czy potrzebny jest shield
        if(change < 0 && myrank <= 25)
        {
          if(myrank <= 5)
          {
            change = change*0.1;
          }
          else if(myrank > 5 && myrank <= 10)
          {
            change = change*0.2;
          }
          else if(myrank > 10 && myrank <= 15)
          {
            change = change*0.4;
          }
          else if(myrank > 15 && myrank <= 20)
          {
            change = change*0.6;
          }
          else if(myrank > 20 && myrank <= 25)
          {
            change = change*0.8;
          }
          
        }
        //Nowe PP wpiszmy w nowy array bo nie kończymy ze sprawdzaniem graczy.
        int changeint = Convert.ToInt16(Math.Floor(change));
        pp_after[i] = pp_before[i]+changeint;
        // Jeżeli gracz spadł poniżej 0, wyzeruj konto
        if(pp_after[i] < 0)
        {
          pp_after[i] = 0;
        }
        // Jeżeli gracz spadł poniżej minimum, ustaw minimum.
        if(pp_after[i] < pp_minimum[i])
        {
          pp_after[i] = pp_minimum[i];
        }
        if(change > 0) 
        {
          Console.WriteLine(players[i]+" zdobył "+changeint+"pp");
        }
        else if(change < 0)
        {
          Console.WriteLine(players[i]+" stracił "+changeint+"pp");
        }
      }
    } 
    Console.WriteLine("");
    Console.WriteLine("// Ranking po wyścigu //");
    {
      for(int i=0; i<pp_after.Length; i++)
      {
        int rank = GetPlayerRank(PP, pp_after[i]);
        int needed = PP[rank] - pp_after[i];
        int difference = pp_after[i]-pp_before[i];
        if(difference >= 0)
        {
          Console.WriteLine("["+rank+"] "+players[i]+"    "+pp_after[i]+"pp (+"+difference+"pp).    Awans za "+needed+"pp");
        }
        else
        {
          Console.WriteLine("["+rank+"] "+players[i]+"    "+pp_after[i]+"pp ("+difference+"pp).   Awans za "+needed+"pp");
        }
      }
    }
	}
}