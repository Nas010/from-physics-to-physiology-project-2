# Uitleg bij alfa tegen tijd

Deze grafiek gebruikt dezelfde doorsnede als de profielgrafiek van Roos. Voeg de PNG of SVG naar wens toe aan de huidige groepspresentatie.

## Spreektekst, ongeveer 50 seconden

Hier zien we de momentumcorrectiefactor alfa uitgezet tegen de tijd, voor dezelfde doorsnede van onze gezonde aorta op ongeveer 199 millimeter vanaf de inlaat. Alfa geeft aan hoe de verdeling van de axiale snelheid de momentumflux beïnvloedt. Bij een uniforme snelheid is alfa één. Voor een Poiseuille-profiel is alfa vier derde, zoals de oranje stippellijn laat zien.

Bij piekflow, rond 0,094 seconde, is alfa ongeveer 1,06. Later wordt alfa ongeveer 1,20 bij 0,234 seconde en 3,60 bij 0,281 seconde. De gemeten waarde blijft dus niet constant gedurende de cyclus. Een vaste alfa beschrijft deze tijdsafhankelijkheid niet volledig.

De sterke stijging vlak voor het lege gebied moeten we voorzichtig interpreteren. In de formule delen we door de netto volumestroom in het kwadraat. Als die klein wordt, kan alfa sterk toenemen, ook doordat lokale heen- en terugstroming elkaar in de netto flow opheffen. Daarom laten we alfa weg zodra de absolute netto flow kleiner wordt dan vijf procent van de lokale piekflow. Het lege gebied betekent dus dat we die verhouding daar niet betrouwbaar interpreteren.

## Waarden en interpretatie

- Model 0012_H_AO_H, doorsnede 46, s = 198,998 mm.
- Eén cyclus duurt 0,937 s. De x-as geeft tijd in seconden, geen dagtijd.
- 201 tijdstippen, waarvan 68 een weergegeven alfa hebben. De 133 weggelaten waarden liggen van 0,290470 tot en met 0,908890 s.
- Alfa is dimensieloos. De grafiek heeft een lineaire y-as en vult ontbrekende waarden niet op.
- Een grotere alfa beschrijft de verhouding tussen de werkelijke axiale momentumflux en de benadering op basis van netto flow. Het is geen maat voor secundaire stroming, turbulentie of ziekte.
- Deze figuur toetst de exacte aanname van een constante alfa op deze doorsnede. Een constante alfa blijft een mogelijke modelbenadering. De figuur bepaalt niet welke constante de beste benadering is voor een volledig 1D-model.
- Voor de definitie geldt alfa = A ∫ u_s² dA / Q². De integraal gebruikt oppervlakgewichten.

Bron: de bestaande section metrics uit het notebook. De onderliggende simulatie en maskering zijn niet veranderd. De oude 7,1%-waarde voor in-plane RMS gaat over een andere grootheid dan alfa.

Alfa kan afhangen van plaats en tijd. Deze grafiek toont alfa(t) op één doorsnede. De figuur met profielvorm en wrijving langs het vat toont alfa(s) bij één gemeenschappelijke fase.
