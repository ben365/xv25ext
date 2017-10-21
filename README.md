# Commande à distance du robot aspirateur Neato XV-25 avec un Raspberry Pi (archive) #

![intro](https://raw.githubusercontent.com/ben365/xv25ext/master/images/dscn0791.jpg)

## Avant propos et objectifs ##

Voilà quelques mois que je suis l'heureux possesseur du robot aspirateur [Neato XV-25](http://www.neatorobotics.com/eur_fr/product/xv-25/).

Sur les conseils de mon ami [milk](http://milk.lekeux.net/fr/) et souhaitant acheter un robot de qualité, efficace contre les poils de chat, pas trop bruyant et pouvant être programmé par un port facilement accessible (USB), je suis ravi de ce choix.

Son utilisation est simple, pour lancer un nettoyage (comme la majorité des robots aspirateurs ) il faut programmer un horaire de nettoyage par jour de la semaine.

Le problème à l'usage, c'est qu'il arrive de temps en temps d'oublier de le programmer, et de se dire une fois sortis de chez soi, “mince j'aurais du le programmer pour qu'il aspire maintenant” !

![chat](https://raw.githubusercontent.com/ben365/xv25ext/master/images/dscn0802.jpg)

**L'idée est donc d'ajouter une fonctionnalité qui permettrait de le lancer en direct à distance via Internet mais aussi de changer le planning via un site web.**

Pour cela je vais utiliser un mini ordinateur Raspberry Pi (RPI) en Wifi, connecté en USB à l'aspirateur et via son [API](http://www.neatorobotics.com/programmers-manual/) lancer des nettoyages.

Les possibilités de cette API sont multiples (déplacement des moteurs, valeurs des capteurs, etc..), on peut facilement imaginer créer un robot en utilisant le socle du XV-25 pour faire tout autre chose, mais mon objectif consiste à garder sa fonction principale : passer l'aspirateur !

## Quelques tests avant de commencer... ##

En se basant sur les essais déjà réalisés par [milk](http://milk.lekeux.net/neato-xv-25/) je vais essayer de me connecter sur le port USB du robot.

Avec l'outil minicom: 

```
# minicom -D /dev/ttyACM0

help
Help Strlen = 1792
Help - Without any argument, this prints a list of all possible cmds.
With a command name, it prints the help for that particular command
Clean - Starts a cleaning by simulating press of start button.
DiagTest - Executes different test modes. Once set, press Start button to engage. (Test modes are mutually exclusive.)
GetAccel - Get the Accelerometer readings.
GetAnalogSensors - Get the A2D readings for the analog sensors.
GetButtons - Get the state of the UI Buttons.
GetCalInfo - Prints out the cal info from the System Control Block.
GetCharger - Get the diagnostic data for the charging system.
GetDigitalSensors - Get the state of the digital sensors.
GetErr - Get Error Message.
GetLDSScan - Get scan packet from LDS.
GetMotors - Get the diagnostic data for the motors.
GetSchedule - Get the Cleaning Schedule. (24 hour clock format)
GetTime - Get Current Scheduler Time.
GetVersion - Get the version information for the system software and hardware.
GetWarranty - Get the warranty validation codes.
PlaySound - Play the specified sound in the robot.
RestoreDefaults - Restore user settings to default.
SetFuelGauge - Set Fuel Gauge Level.
SetMotor - Sets the specified motor to run in a direction at a requested speed. (TestMode Only)
SetTime - Sets the current day, hour, and minute for the scheduler clock.
SetLED - Sets the specified LED to on,off,blink, or dim. (TestMode Only)
SetLCD - Sets the LCD to the specified display. (TestMode Only)
SetLDSRotation - Sets LDS rotation on or off. Can only be run in TestMode.
SetSchedule - Modify Cleaning Schedule.
SetSystemMode - Set the operation mode of the robot. (TestMode Only)
TestMode - Sets TestMode on or off. Some commands can only be run in TestMode.
Upload - Uploads new program to the robot.
```

Bon maintenant essayons de lancer un nettoyage: 
`Clean`

 Il se réveille ! mais il ne se passe rien.. On renvoi la commande:
 `Clean`
 
Là j'ai un message d'erreur sur l'écran LCD qui indique “Débranchez mon câble USB qd vs voulez le nettoyage ”

Hum,… ça va être embêtant pour lancer un nettoyage à distance !

Remarque on peut aussi avoir ce message avec la commande GetErr: 

```
GetErr
220 - Débranchez mon câble USB qd vs voulez le nettoyage 
```

Essayons de voir ce que ça donne en éteignant le Raspberry Pi, si on fait un halt est-ce suffisant ? Nada.. Le port USB est toujours sous tension même quand le RPI est éteint et le nettoyage ne se lance pas..

Par contre si on enlève l’alimentation du Raspberry Pi, **Bingo !** le nettoyage se lance sans pour autant débrancher le câble USB !

Conclusion, il va falloir trouver un moyen pour que le Raspberry Pi se coupe lui-même de son alimentation pour lancer le nettoyage.

J'ai fait quelques recherches sur comment contrôler l'alimentation des ports USB par logiciel, en vain..

Je vais donc réaliser cette coupure avec un montage électronique externe. 

## Stratégie d'alimentation ##

Le robot fonctionne avec un chargeur qui délivre une tension de 24V. 

![tension](https://raw.githubusercontent.com/ben365/xv25ext/master/images/dscn0789.jpg)

 Pour alimenter notre Raspberry Pi nous allons utiliser cette source d’énergie et l'adapter à 5V.
 
 ## Battery or not battery... ##
 
J'ai commencé par faire des essais avec une batterie: cela prend de la place sur l'aspirateur et induit une complexité supplémentaire.

J'ai fait le choix de ne donc pas utiliser de batterie, je commanderais donc le robot uniquement quand il sera sur sa base. Pour remplir mes objectifs, ce mode de fonctionnement est suffisant.

## Régulateur de tension ##

![lm2596](https://raw.githubusercontent.com/ben365/xv25ext/master/images/lm2596.jpg)

Je l'avais acheté sur Ebay, à un vendeur en Chine, ces modules sont très bon marché et très pratique. 
 
 ![dscn0795.jpg](https://raw.githubusercontent.com/ben365/xv25ext/master/images/dscn0795.jpg)
 ![dscn0793.jpg](https://raw.githubusercontent.com/ben365/xv25ext/master/images/dscn0793.jpg)
 ![dscn0794.jpg](https://raw.githubusercontent.com/ben365/xv25ext/master/images/dscn0794.jpg)
 
Celui que je possède à deux particularités intéressantes:

* Une LED qui indique qu'il est sous tension et en fonctionnement.
* Une sortie de la broche on/off du LM2596.

En regardant sur Ebay, je constate que cette broche n'est pas souvent exposée sur les modules, mais il suffit d'utiliser la broche 5 du composant en enlevant sa mise à la masse (conformément à la [documentation du composant](http://www.ti.com/lit/ds/symlink/lm2596.pdf)).

Cette broche va en effet nous permettre de couper l'alimentation du Raspberry Pi à l'aide d'une sortie du GPIO. 
 
## Auto-extinction du Raspberry Pi ##

**Obsolète, la solution la plus efficace consiste à couper la connexion USB**

Pour réaliser cette opération je vais donc utiliser la broche ON/OFF du LM2596. Cette entrée permet de couper le régulateur lorsqu'elle reçoit un état logique “1”. 

### Premier test ###

Aller hop, je branche une sortie du GPIO (4), c'est à dire la broche 7 (cf schéma suivant), sur cette entrée et j'envoie un “1” dessus (pas de soucis de masse elle est commune).

![gpios.png](https://raw.githubusercontent.com/ben365/xv25ext/master/images/gpios.png)

```
# echo "4" > /sys/class/gpio/export
# echo "out" > /sys/class/gpio/gpio4/direction
# echo "1" > /sys/class/gpio/gpio4/value
```

ça marche !! Yeah, le Raspberry reboot..

Sauf que ça parait bien bref comme coupure…. Logique au redémarrage de RPI l'état de sortie de GPIO4 ne reste pas à “1”.

Essayons de voir si ça suffit pour lancer un nettoyage en simulant le débranchement de l'USB.. 

```
# minicom -D /dev/ttyACM0
clean
```

Attention si l'on ferme la session sur le port série la commande Clean est annulée, il faut donc lancer un deuxième shell en parallèle pour envoyer la commande au GPIO. 

```
# echo "4" > /sys/class/gpio/export
# echo "out" > /sys/class/gpio/gpio4/direction
# echo "1" > /sys/class/gpio/gpio4/value
```

Bon ça ne fonctionne pas..

Deuxième problème si on laisse branché GPIO4 sur on/off du LM2596 ça ne démarre plus car GPIO4 est à High au démarrage du RPI. Le problème ne se pose pas sur le GPIO17 mais le problème reste le même pour lancer un nettoyage.

### Ajout d'un timer à base de 555 ###

**Obsolète, la solution la plus efficace consiste à couper la connexion USB**

**Un monostable est suffisant pour le lancement d'un nettoyage en direct à distance, par contre pour permettre la planification à distance il faut plutôt utiliser un montage flip/flop.**

![xv25ext.png](https://raw.githubusercontent.com/ben365/xv25ext/master/images/xv25ext.png)

Afin de provoquer une coupure de l'alimentation du Raspberry-Pi de plusieurs secondes je vais utiliser un mini montage électronique monostable à base de d'un TS555.

![dscn0797.jpg](https://raw.githubusercontent.com/ben365/xv25ext/master/images/dscn0797.jpg)
![dscn0798.jpg](https://raw.githubusercontent.com/ben365/xv25ext/master/images/dscn0798.jpg)

L'idée consiste à envoyer une commande de coupure via le GPIO qui sera prolongée de plusieurs secondes grâce au monostable sur l'entrée Off de régulateur de tension.

![xv25extdia.jpeg](https://raw.githubusercontent.com/ben365/xv25ext/master/images/xv25extdia.jpeg)

**Attention : le monostable doit être compatible aux tensions CMOS 3.3V, sinon c'est le RPI qui fume !**

Pour cela j'ai utilisé la version CMOS du fameux NE555, le TS555.

Pour plus de détails je vous conseille la lecture de cette page: http://www.electronicsclub.info/555timer.htm.

Pour obtenir une durée de 20 secondes environ (j'ai prévu large) j'ai utilisé un condensateur de 10uF et une résistance de 150kOhm. 

**Note importante**: L'entrée du trigger est mise à la masse avec un condensateur de 100nF, cela permet d'activer la pulsation de 20s à la mise sous tension. Ce détail est important, cela évite les micro-coupures sur le Raspberry-Pi lorsqu'il revient sur sa base. En effet lorsqu'il se repositionne sur son chargeur le robot à tendance à avoir quelques hésitations et l'alimentation bagotte un peu.

En activant le trigger à la mise sous tension, le RaspBerry Pi ne démarre que 20s après l'arrivé à la base. A ce stade la position est stabilisé. 

### Ajout d'un flip/flop à base de 555 à la place du monostable ###

**Obsolète, la solution la plus efficace consiste à couper la connexion USB**

 Après quelques jours d'essai et d'utilisation, en codant une page web pour faire de la planification à distance je me suis heurté à un autre problème: le RPI doit également être éteint avant qu'un nettoyage planifié se lance.

Un signal HIGH sur le GPIO va alors couper l’alimentation indéfiniment. En positionnant un RESET à la mise sous tension (pour permettre le lancement du RPI) cette solution fonctionne parfaitement pour un lancement à distance en direct mais également pour un lancement via planification.

En effet en programmant une extinction du RPI quelques minutes avant le nettoyage, celui-ci se lancera sans le problème du câble USB branché.

Le schéma du flip/flop est très similaire au monostable, il suffit d'enlever le circuit RC de charge et de déconnecter les broches 6 et 7 du TS555. 

![xv25extflipflop.png](https://raw.githubusercontent.com/ben365/xv25ext/master/images/xv25extflipflop.png)

### Coupure du port USB ###

 Après plusieurs tentatives, je pense avoir trouvé The solution pour simuler le débranchement du câble USB pour lancer un nettoyage à distance.

Mon idée départ était de couper l’alimentation du RPI. En effet après avoir remarqué qu'une fois le RPI éteint électriquement le port USB était considéré comme débranché par le XV25, j'ai réalisé une commande à base de timer pour que le RPI s’auto-désalimente à l'aide du GPIO.

En fait le but étant de déconnecter le câble USB la solution la plus simple et fiable et plutôt de s'attaquer à l’alimentation du câble plutôt que le RPI.

Pour cela j'ai réalisé un mini montage à base d'un photocoupleur 4N25. La commande du photocoupleur se fait à l'aide du GPIO et la sortie collecteur-émetteur simule un branchement de l’alimentation USB (+5V).

En effet, si le +5V est absent aux bornes du port USB du XV25 alors celui considère le câble branché. La diode est émettrice du photocoupleur est alimentée par le GPIO pour indiquer un branchement du câble USB. Avant chaque envoi de commande au robot il sera nécessaire d'ouvrir le port à l'aide d'un signal sur le GPIO puis de le fermer en envoyant un 0.

Une résistance est nécessaire à l'entrée du photocoupleur 4N25 : les valeurs max de la diode sont VFmax 1.5V et Imax 50mA.

Avec une tension de 3.3V au sortie du GPIO, on a VR (tension au borne de la résistance) = 3,3 - 1,5 = 1,8V. U = R * I. R = U / I, R = 1,8 / 0.05 = 36 Ohm. C'est la valeur minimum pour donner un ordre de grandeur. Avec 100 Ohm ça fonctionne. 

![xv254n25.png](https://raw.githubusercontent.com/ben365/xv25ext/master/images/xv254n25.png)

## Test final ##

Une fois les différents éléments connectés nous pouvons vérifier que ça fonctionne:

 * Branchement du robot sur sa base
 * ~~Une attente de 20s se déclenche (en version monostable)~~
 * le Raspberry Pi démarre
 * J'ouvre une session SSH et connecte l’alimentation du port USB en envoyant la valeur “1” au GPIO 17 (entrée du photocoupleur)
    quelques secondes plus tard je lance minicom et la commande Clean
 * Le robot attend que je débranche
 * J'ouvre une deuxième session SSH et positionne la sortie du GPIO à “0” pour couper l'alimentation du port USB
 * ~~Le timer (ou flip/flop) se déclenche, 2-3 secondes plus tard le robot détecte le débranchement de l'USB et démarre le nettoyage.~~
 * Hourra !!
 
## Installation et configuration de Arch Linux sur Raspberry Pi ##

![arch-linux-logo.png](https://raw.githubusercontent.com/ben365/xv25ext/master/images/arch-linux-logo.png)
![raspberrypi.jpg](https://raw.githubusercontent.com/ben365/xv25ext/master/images/raspberrypi.jpg)

## Installation de l'image ##

Télécharger l'image et vérifier le md5: 

```
$ wget http://archlinuxarm.org/os/ArchLinuxARM-rpi-latest.zip
$ wget http://archlinuxarm.org/os/ArchLinuxARM-rpi-latest.zip.md5
$ md5sum ArchLinuxARM-rpi-latest.zip
$ cat ArchLinuxARM-rpi-latest.zip.md5
```

Identifier votre carte SD sur votre PC: 

```
~$ lsblk
NAME        MAJ:MIN RM   SIZE RO TYPE MOUNTPOINT
sda           8:0    0 119,2G  0 disk 
├─sda1        8:1    0   243M  0 part /boot
├─sda2        8:2    0   1,4G  0 part 
└─sda3        8:3    0 117,6G  0 part /
sr0          11:0    1  1024M  0 rom  
mmcblk0     179:0    0   7,4G  0 disk 
├─mmcblk0p1 179:1    0    90M  0 part 
├─mmcblk0p2 179:2    0     1K  0 part 
└─mmcblk0p5 179:5    0   1,7G  0 part 
```

Ici le device sd card est **/dev/mmcblk0**.

Décompression de l'archive:

```
$ unzip ArchLinuxARM-rpi-latest.zip
Archive:  ArchLinuxARM-rpi-latest.zip
  inflating: ArchLinuxARM-2014.02-rpi.img 
```

Installation de la carte (en root): 

```
# dd bs=1M if=/home/ben/ArchLinuxARM-2014.02-rpi.img of=/dev/mmcblk0
1870+0 enregistrements lus
1870+0 enregistrements écrits
1960837120 octets (2,0 GB) copiés, 164,571 s, 11,9 MB/s
# sync
```

Ensuite on démarre le Raspberry Pi avec la carte connectée en Ethernet sur son réseau local (dhcp avec internet). 

### Installation du Wifi ###

Se connecter en ssh en utilisant mdns: 

`ssh root@alarmpi.local`

*Se connecter avec le mot de passe par défaut “root”.*

Installer le wifi avec wpa_supplicant: 
```
[root@alarmpi ~]# wpa_passphrase Livebox-XXXX 'makeywifipreviate' > /etc/wpa_supplicant/wpa_supplicant-wlan0.conf
[root@alarmpi ~]# systemctl enable wpa_supplicant@wlan0
ln -s '/usr/lib/systemd/system/wpa_supplicant@.service' '/etc/systemd/system/multi-user.target.wants/wpa_supplicant@wlan0.service'
[root@alarmpi ~]# systemctl enable dhcpcd@wlan0
ln -s '/usr/lib/systemd/system/dhcpcd@.service' '/etc/systemd/system/multi-user.target.wants/dhcpcd@wlan0.service'
[root@alarmpi ~]# reboot
```

 Voilà le Rasberry Pi démarre automatiquement en wifi sur le réseau :) 
 
### Configurer SSH ###
 
Nous allons maintenant installer une clé ssh pour ne plus saisir de mot de passe: 
```
$ ssh-keygen -t rsa -b 1024
$ cat ~/.ssh/id_rsa.pub | ssh root@alarmpi.local "mkdir -p ~/.ssh && cat - >> ~/.ssh/authorized_keys"
root@192.168.1.15's password:
$  ssh root@alarmpi.local
Welcome to Arch Linux ARM

     Website: http://archlinuxarm.org
       Forum: http://archlinuxarm.org/forum
         IRC: #archlinux-arm on irc.Freenode.net

Last login: Wed Dec 31 17:03:59 1969 from pc1.home
```

__Remarque général__: il s'agit d'une plate-forme de développement, la sécurité n'est pas une priorité.

### Configurer la date et l'heure ###

**Il est indispensable que Raspberry Pi soit à l'heure notamment pour pouvoir vérifier les certificats SSL correctement.**

Mettre à l'heure avec ntp:

`[root@alarmpi ~]# usr/bin/ntpd -qg -u ntp:ntp`

Vérifier le fuseau horraire:

```[root@alarmpi ~]# timedatectl status | grep Timezone
Timezone: America/Denver (MST, -0700)```

Chercher le fuseau horaire de la France:

```[root@alarmpi ~]# timedatectl list-timezones | grep Paris
Europe/Paris```

Positionner le bon fuseau:

`[root@alarmpi ~]# timedatectl set-timezone Europe/Paris`

Vérifier que la date est bonne:

```[root@alarmpi ~]# date
Wed Feb 12 23:19:51 CET 2014```

Activer ntpd au démarage:

`[root@alarmpi ~]# systemctl enable ntpd.service`

Mise à jour du système

`[root@alarmpi ~]# pacman -Syu`

à exécuter plusieurs fois si nécessaire après reboot (mise à jour kernel ou système de base) jusqu'à obtenir:

```[root@alarmpi ~]# pacman -Syu
:: Synchronizing package databases...
 core is up to date
 extra is up to date
 community is up to date
 alarm is up to date
 aur is up to date
:: Starting full system upgrade...
 there is nothing to do
 ```

Mes petits oignions (facultatif)

Bon il est temps de mettre de la couleur et mes outils préférés pour travailler en console :)

Git et Vim d'abord !

`[root@alarmpi ~]# pacman -S git vim`

Vérifions l'accès à mes pages web à travers SSL avec lynx et les certificats racines:

```[root@alarmpi ~]# pacman -S lynx ca-certificates

[root@alarmpi ~]# lynx https://systemd.info/wiki
```

Cool ça marche !

maintenant je récupère mes dotfiles:

`[root@alarmpi ~]# git clone https://systemd.info/code/dotfiles/`

avec ses sous modules:

```cd dotfiles
[root@alarmpi dotfiles]# git submodule init
[root@alarmpi dotfiles]# git submodule update --recursive```

et on crée les raccourcis:

```
[root@alarmpi dotfiles]# ./makesymlinks.sh
[root@alarmpi dotfiles]# echo "source ~/.bashrc" >> ~/.profile
```

on se reconnecte et chouette de la couleur !

Outils de base pour communication série

`pacman -S minicom`

Installation de python

Pour piloter le robot nous allons utiliser le langage python, c'est simple, puissant et j'aime bien !

`# pacman -S python python-pip base-devel`

Installation de pyserial pour communiquer avec le robot sur le port série (simuler via USB).

`pip install pyserial`

Attention: Si vous n'avez pas mis à l'heure la machine pip fonctionnant via SSL, il ne fonctionnera pas.

Installons maintenant le module d'accès au GPIO du RPI:

`pip install RPi.GPIO`

## Codes ##

### Objectif ###

Le but est de réaliser une interface web qui permet de lancer l'aspirateur à distance. Voici une liste des fonctionnalités à coder:

* Script qui lance le nettoyage (fait)
   * Interface web
   * pour lancer un nettoyage
   * programmer les planifications
* Interfaçage avec le système de communication par SMS

Prévoir l’arrêt du Raspberry Pi avant le lancement normal avec la planification pour ne pas bloquer l'usage classique par la présence du câble USB.
Sources

Tous les codes sont sur le dépôt [XV25Ext](https://github.com/ben365/xv25ext/).

### Interface web avec Flask ###

![webui.png](https://raw.githubusercontent.com/ben365/xv25ext/master/images/webui.png)

Le cœur du programme fonctionne à l'aide d'une interface web que j'ai réalisé avec le framework [Flask](http://flask.pocoo.org/).

Le code source est ici : https://github.com/ben365/xv25ext/blob/master/webcommand.py 

### Approche globale ###

Le serveur web est lancé avec [Gunicorn](http://gunicorn.org/).

Son lancement automatique se fait avec [ce script systemd](https://github.com/ben365/xv25ext/blob/master/xv25ext.service):

```
[Unit]
Description=XV25 remote command

[Service]
ExecStart=/usr/bin/gunicorn -b 0.0.0.0:8000 -D --chdir /root/xv25ext/ webcommand:app
Type=forking
User=root
Restart=always
StandardOutput=syslog
StandardError=syslog
WorkingDirectory = /root/xv25ext/

[Install]
WantedBy=multi-user.target
```

 La lecture des schedules permet de pré-remplir le formulaire de planification.

Une action sur le bouton “Enregistrer” va récupérer les planifs et les saisir dans le robot. 

[reverseProxied.py](https://github.com/ben365/xv25ext/blob/master/reverseProxied.py) permet d'utiliser le serveur derrière nginx. 

~~syncstoprpi.py est un script appelé toutes les 5 minutes afin de lire la planification du jour enregistrée dans le robot, et programmer une tache cron (avec python-crontab) pour éteindre le RPI 3 minutes avant celle-ci.~~

Chaque envoi de commande est réalisé après l'activation de l’alimentation du port USB et se termine par la coupure du port USB. Ainsi le nettoyage peut se lancer sans se bloquer sur le message « Veuillez me débrancher. »

Le code n'est pas très optimisé ni très joli (écrit tard le soir, en 2-3 soirées), mais il fonctionne !

Et voilà !
