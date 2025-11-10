import time
import subprocess
import Jetson.GPIO as GPIO
import curses
import threading

# ==============================================================================
# 1. CONFIGURATION DES BROCHES ET CONSTANTES
# ==============================================================================
# --- Broches GPIO (numérotation BOARD) ---
LED_PIN_GREEN = 15      # Indicateur de marche (ON/OFF)
LED_PIN_RED = 31        # Indicateur de Mute
LED_PIN_REC = 29        # Indicateur d'enregistrement (clignotant)
BUTTON_OnOff_PIN = 13
BUTTON_incVolume_PIN = 16
BUTTON_decVolume_PIN = 18
BUTTON_register_PIN = 22
BUTTON_mute_PIN = 7


# --- Système audio ---
# arecord -l && aplay -l <-- commande bash
MICROPHONE="plughw:ATR4650USB"  # Micro ATR4650USB (carte 3, périphérique 0)
SPEAKER="hw:2,0"     # Haut-parleur ASK130 (carte 2, périphérique 0)

MICROPHONE_CARD="3"     # Le numéro de la carte (hw:3,0 -> carte 3)
MUTE_CONTROL_NAME="Mic" # Nom pour le contrôle d'entrée

ENREGISTREMENT_FILE = "/home/labo/my_whisper_project/test_jetson_led/enregistrement.wav" 

# --- Paramètres du Volume ---
VOLUME_LEVELS = [0, 20, 40, 60, 80, 100]

# --- Dictionnaire de langues ---
dico_language = {
    "Français": "fr", "English": "en", "Español": "es", "Deutsch": "de",
    "Italiano": "it", "Português": "pt", "Polski": "pl", "Русский": "ru", "Türkçe": "tr",
}
menu_items = list(dico_language.keys())
menu_items.append("Quitter")


# ==============================================================================
# 2. ÉTAT GLOBAL DE L'APPAREIL (LA MÉMOIRE)
# ==============================================================================
# Ces variables définissent l'état actuel de l'appareil.
is_device_on = False
is_recording = False
recording_process = None
audio_passthrough_process = None # Processus pour le passthrough audio
is_muted = False
current_level = 2  # Niveau de volume initial (40%)
language1 = "Non défini"
language2 = "Non défini"
keep_running = True

# Le "verrou" pour empêcher les conflits entre les appuis de boutons simultanés
state_lock = threading.Lock()


# ==============================================================================
# 3. FONCTIONS UTILITAIRES (OUTILS)
# ==============================================================================
def update_volume_display():
    """Affiche la barre de volume actuelle dans le terminal."""
    if not is_device_on: return
    
    volume_percent = VOLUME_LEVELS[current_level]
    command = f"amixer -c {MICROPHONE_CARD} set '{MUTE_CONTROL_NAME}' capture {volume_percent}%"
    subprocess.run(command, shell=True)
    bar_length = len(VOLUME_LEVELS) - 1
    bar = "#" * current_level + "-" * (bar_length - current_level)
    print(f"\nVolume : Niveau {current_level} ({volume_percent}%) [{bar}]")

def blinking_led_thread():
    """
    Fonction qui s'exécutera en parallèle pour faire clignoter la LED.
    Elle s'arrêtera quand la variable globale is_recording passera à False.
    """
    global is_recording

    while is_recording:
        GPIO.output(LED_PIN_REC, GPIO.HIGH)
        time.sleep(0.5)
        # On re-vérifie la condition au cas où elle aurait changé pendant le sleep
        if not is_recording: break
        GPIO.output(LED_PIN_REC, GPIO.LOW)
        time.sleep(0.5)

    # Nettoyage : s'assurer que la LED est éteinte à la fin
    GPIO.output(LED_PIN_REC, GPIO.LOW)


# ==============================================================================
# 4. FONCTIONS DE CALLBACK (RÉACTIONS AUX BOUTONS)
# ==============================================================================
def on_off_callback(channel):
    global is_device_on, is_muted, keep_running
    with state_lock:
        is_device_on = not is_device_on  # On inverse l'état ON/OFF

        if is_device_on:
            GPIO.output(LED_PIN_GREEN, GPIO.HIGH)
            print("\n>> Appareil ALLUMÉ <<")
            start_passthrough_process()
        else:
            # Si on éteint, tout le reste s'éteint aussi
            GPIO.output(LED_PIN_GREEN, GPIO.LOW)
            GPIO.output(LED_PIN_RED, GPIO.LOW)
            # Arrête le clignotement si on éteint l'appareil
            stop_recording_process() # Assure que l'enregistrement est arrêté
            stop_passthrough_process()
            is_muted = False
            print("\n>> Appareil ÉTEINT <<")
            keep_running = False

def volume_up_callback(channel):
    global current_level
    with state_lock:
        if not is_device_on:
            print("(Appareil éteint, volume bloqué)")
            return
        
        if current_level < len(VOLUME_LEVELS) - 1:
            current_level += 1
            update_volume_display()

def volume_down_callback(channel):
    global current_level
    with state_lock:
        if not is_device_on:
            print("(Appareil éteint, volume bloqué)")
            return
            
        if current_level > 0:
            current_level -= 1
            update_volume_display()

def mute_callback(channel):
    global is_muted
    with state_lock:
        if not is_device_on:
            print("(Appareil éteint, mute bloqué)")
            return
            
        is_muted = not is_muted
        GPIO.output(LED_PIN_RED, GPIO.HIGH if is_muted else GPIO.LOW)
  
       # --- LOGIQUE DE MUTE VIA SUBPROCESS (Liste d'arguments, la plus fiable) ---
        state = "off" if is_muted else "on"
        
        # 1. Commande pour l'interrupteur Mute ('on'/'off')
        command_list = [
            "amixer", 
            "-c", MICROPHONE_CARD, 
            "set", MUTE_CONTROL_NAME,  # 'Mic'
            "capture",                 # Fonction ciblée
            state
        ]
        
        try:
            # Exécution SANS shell=True
            subprocess.run(command_list, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            print(f"\n>> Mute {'ACTIVÉ' if is_muted else 'DÉSACTIVÉ'} ({MUTE_CONTROL_NAME} capture set à {state}) <<")
            
        except subprocess.CalledProcessError as e:
            # Affichage de la commande exacte qui a échoué
            print(f"ÉCHEC MUTE! Commande: {' '.join(e.cmd)} | Statut: {e.returncode}")
        except FileNotFoundError:
            print("Erreur: Le programme 'amixer' n'est pas trouvé. Est-il installé et dans le PATH?")


def register_callback(channel):
    global is_recording, recording_thread, recording_process
    
    with state_lock:
        if not is_device_on:
            print("(Appareil éteint, enregistrement impossible)")
            return
        
        # --- LOGIQUE D'ARRÊT ---
        if is_recording:
            stop_recording_process()
            print("\n>> Enregistrement ARRÊTÉ. Fichier 'enregistrement.wav' sauvegardé. <<")
            
        # --- LOGIQUE DE DÉMARRAGE ---
        else:
            is_recording = True
            
            # Commande arecord à lancer en arrière-plan
            command = ["arecord", "-D", MICROPHONE, "-f", "cd", "-t", "wav", ENREGISTREMENT_FILE]
            
            try:
                # Démarrer le processus d'enregistrement (Popen = non bloquant)
                recording_process = subprocess.Popen(command, 
                                                     stdout=subprocess.DEVNULL, 
                                                     stderr=subprocess.DEVNULL)
                
                print(f"\n>> Enregistrement DÉMARRÉ... <<")
                
                # Démarrage du thread pour la LED clignotante (votre code existant)
                recording_thread = threading.Thread(target=blinking_led_thread)
                recording_thread.start()
                
            except Exception as e:
                print(f"Erreur lors du démarrage de l'enregistrement : {e}")
                is_recording = False # Réinitialiser l'état en cas d'échec


def stop_recording_process():
    """Arrête le processus arecord en cours de la manière la plus simple."""
    global recording_process, is_recording
    
    if recording_process and recording_process.poll() is None:
        print("Arrêt du processus arecord...")
        # Envoie un signal d'arrêt (la manière la plus propre)
        recording_process.terminate() 
        recording_process.wait(timeout=1) # Attend un peu la fin
        recording_process = None
    
    is_recording = False # Mise à jour de l'état global
    

def start_passthrough_process():
    """Démarre le flux audio continu (Micro -> Speaker) via une commande pipe shell."""
    global audio_passthrough_process
   
    command = f"arecord -D {MICROPHONE} -f cd -t raw - | aplay -D {SPEAKER} -f cd -t raw" # On utilise 'raw' et un format simple (-f cd est 16bit, 44.1kHz, stereo)
    #command = f"arecord -D {MICROPHONE} -f cd -t wav -r 16000 -c 1 output.wav - | aplay output.wav -D {SPEAKER} -r 16000" # On utilise 'raw' et un format simple (-f cd est 16bit, 44.1kHz, stereo)
    
    print("Démarrage de l'audio continu...")
    try:
        audio_passthrough_process = subprocess.Popen(
            command, 
            shell=True,
            stdout=subprocess.DEVNULL, # Ne pas afficher les logs dans la console
            stderr=subprocess.DEVNULL
        )
    except Exception as e:
        print(f"Erreur lors du démarrage : {e}")
        audio_passthrough_process = None


def stop_passthrough_process():
    global audio_passthrough_process

    if audio_passthrough_process and audio_passthrough_process.poll() is None:
        print("Arrêt du Pass-through audio continu...")
        # Tuer les processus aplay et arecord lancés en arrière-plan, ATTENTION à bein couper l'enregistrement avant d'appeler cette fonction
        subprocess.run("pkill -9 aplay", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run("pkill -9 arecord", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Mettre à jour la variable de référence
        audio_passthrough_process = None
    
# ==============================================================================
# 5. INITIALISATION ET BOUCLE PRINCIPALE
# ==============================================================================
try:
    # --- Configuration des broches ---
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup([LED_PIN_GREEN,LED_PIN_REC, LED_PIN_RED], GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup([BUTTON_OnOff_PIN, BUTTON_incVolume_PIN, BUTTON_decVolume_PIN, 
                BUTTON_register_PIN, BUTTON_mute_PIN], GPIO.IN)

    print("Appareil prêt. Appuyez sur le bouton ON/OFF pour démarrer.")
    
    # --- Détection des appuis sur les boutons ---
    bouncetime = 300 # Anti-rebond de 300ms
    GPIO.add_event_detect(BUTTON_OnOff_PIN, GPIO.FALLING, callback=on_off_callback, bouncetime=bouncetime)
    GPIO.add_event_detect(BUTTON_incVolume_PIN, GPIO.FALLING, callback=volume_up_callback, bouncetime=bouncetime)
    GPIO.add_event_detect(BUTTON_decVolume_PIN, GPIO.FALLING, callback=volume_down_callback, bouncetime=bouncetime)
    GPIO.add_event_detect(BUTTON_mute_PIN, GPIO.FALLING, callback=mute_callback, bouncetime=bouncetime)
    GPIO.add_event_detect(BUTTON_register_PIN, GPIO.FALLING, callback=register_callback, bouncetime=bouncetime)

    # --- Boucle principale ---
    # Le programme attend ici pendant que les callbacks font tout le travail en arrière-plan
    while keep_running:
        time.sleep(1)

except KeyboardInterrupt:
    print("\n\nProgramme arrêté par l'utilisateur.")
finally:
    GPIO.output([LED_PIN_GREEN, LED_PIN_RED, LED_PIN_REC], GPIO.LOW)
    is_recording = False
    stop_recording_process()
    stop_passthrough_process()
    time.sleep(0.6) # Laisse le temps au thread de finir sa dernière boucle
    GPIO.cleanup()
    print("GPIO nettoyés. Fin du programme.")








