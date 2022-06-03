# Enedis Optimize

Compare plans using [data exported from Enedis](https://mon-compte-particulier.enedis.fr/suivi-de-mesures/?ajouter_telechargement=true).

You will need Python 3 as well as `requests` and `colorama`.

It can only take hourly data as input. Linky must be configured to collect data with such precision.

Pricing and off-peak times must be set accordingly. Here, they are set as an example to the current EDF pricing (the three main plans available) and Toulouse off-peak times. Find yours: [EDF](https://particulier.edf.fr/content/dam/2-Actifs/Documents/Offres/Grille_prix_Tarif_Bleu.pdf), [Enedis](https://www.enedis.fr/heures-creuses/standard).

Use `config.sample.json` as a template and fill in your own settings. Name your configuration file `config.json`. The sample configuration features what you can do: a fixed monthly subscription, multiple sets of off-peak times, three modes of calculation (simple unique pricing, standard/off-peak pricing, complex pricing involving and API), and a few other settings.

To use the [RTE API](https://data.rte-france.com/catalog/-/api/consumption/Tempo-Like-Supply-Contract/v1.1), API keys must be provided. Obtain yours by signing in and creating an application.

## Usage

```bash
./enedis_optimize.py Enedis_Conso_Heure_20200501-20220430_00000000000000.csv
```
