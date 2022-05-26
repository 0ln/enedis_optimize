# Enedis Optimize

Compare plans using [data exported from Enedis](https://mon-compte-particulier.enedis.fr/suivi-de-mesures/?ajouter_telechargement=true).

It can only take hourly data as input. Linky must be configured to collect data with such precision.

Pricing and off-peak times must be set accordingly. Here, they are set as an example to the current EDF pricing and Toulouse off-peak times. Find yours: [EDF](https://particulier.edf.fr/content/dam/2-Actifs/Documents/Offres/Grille_prix_Tarif_Bleu.pdf), [Enedis](https://www.enedis.fr/heures-creuses/standard).

## Usage

```bash
./enedis_optimize.py Enedis_Conso_Heure_20200501-20200430_00000000000000.csv
```
