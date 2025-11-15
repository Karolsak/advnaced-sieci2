# Symulator Silników DC - Wersja HTML

Interaktywna aplikacja webowa do analizy silników prądu stałego z dynamiczną wizualizacją i solverami ODE.

## 🚀 Funkcje

### ✨ Kluczowe Możliwości
- **Interaktywne suwaki** - Zmiana parametrów w czasie rzeczywistym
- **Responsywny design** - Automatyczne dopasowanie do rozmiaru okna
- **Dynamiczna symulacja** - Solvery ODE (RK45 i Euler)
- **Wizualizacja Plotly** - Profesjonalne wykresy interaktywne
- **Trzy problemy** - Kompleksowa analiza silników DC

### 📊 Zakładki

#### Problem 1: Silnik Bocznikowy (230V, 11kW)
**Dane:**
- Napięcie zasilania: 230 V
- Moc wejściowa: 11 kW
- Prąd biegu jałowego: 5 A
- Prędkość biegu jałowego: 1150 rpm
- Rezystancja twornika: 0.5 Ω
- Rezystancja wzbudzenia: 110 Ω

**Oblicza:**
- (a) **Moment obrotowy: 86.77 N·m**
- (b) **Sprawność: 80.04%**
- (c) **Prędkość: 1042.40 rpm**

**Wykresy:**
1. Prędkość vs Czas
2. Prąd Twornika vs Czas
3. Moment vs Czas
4. Moc Wyjściowa vs Czas

---

#### Problem 2: Silnik Szeregowy - Prędkość (250V, 18.65kW)
**Dane:**
- Napięcie: 250 V
- Rezystancja twornika: 0.1 Ω
- Rezystancja wzbudzenia: 0.05 Ω
- Spadek napięcia szczotek: 3 V
- Przy 80 A: prędkość = 600 rpm
- Oblicz prędkość przy 100 A

**Wynik:**
- **Prędkość przy 100 A: 471.49 rpm**

**Wykresy:**
1. Prędkość vs Czas (zmiana obciążenia)
2. Prąd vs Czas
3. Moment vs Czas
4. Charakterystyka Prędkość-Prąd

---

#### Problem 3: Silnik Szeregowy - Moment (220V)
**Dane:**
- Napięcie: 220 V
- Początkowa prędkość: 800 rpm
- Początkowy prąd: 100 A
- Oblicz prędkość przy połowie momentu

**Wynik:**
- **Prędkość przy połowie momentu: 1163.96 rpm**

**Wykresy:**
1. Reakcja Prędkości na Redukcję Momentu
2. Prąd vs Czas
3. Moment vs Czas
4. Charakterystyka Moment-Prędkość

---

## 🎯 Jak Używać

### Metoda 1: Otwórz bezpośrednio w przeglądarce
```bash
# Po prostu otwórz plik w przeglądarce
firefox dc_motor_simulator.html
# lub
google-chrome dc_motor_simulator.html
# lub
edge dc_motor_simulator.html
```

### Metoda 2: Lokalny serwer HTTP (zalecane)
```bash
# Python 3
python3 -m http.server 8000

# Następnie otwórz w przeglądarce:
# http://localhost:8000/dc_motor_simulator.html
```

### Metoda 3: Live Server (VS Code)
1. Zainstaluj rozszerzenie "Live Server" w VS Code
2. Kliknij prawym na `dc_motor_simulator.html`
3. Wybierz "Open with Live Server"

---

## 🎮 Sterowanie

### Suwaki
- **Przeciągnij** suwak aby zmienić wartość
- **Kliknij** na slider dla precyzyjnej kontroli
- Wartość aktualizuje się automatycznie

### Pola Wprowadzania
- **Wpisz** wartość liczbową
- Suwak automatycznie się synchronizuje
- Naciśnij Enter aby potwierdzić

### Przyciski
- **🔄 Oblicz i Symuluj** - Uruchamia obliczenia i symulację
- **Zakładki** - Przełącz między problemami

### Solver ODE
- **RK45 (Runge-Kutta)** - Wysoka dokładność, adaptive step size
- **Euler** - Prostsza metoda, szybsza, edukacyjna

---

## 📐 Szczegóły Techniczne

### Równania Różniczkowe

**Silnik Bocznikowy:**
```
dω/dt = (T - B×ω) / J
dIa/dt = (V - Eb - Ia×Ra) / La
Eb = Kt × ω × If
T = Kt × If × Ia
```

**Silnik Szeregowy:**
```
dω/dt = (T - B×ω) / J
dIa/dt = (V - Eb - Ia×(Ra+Rf) - Vb) / (La+Lf)
Eb = φ × ω  (gdzie φ ∝ Ia)
T = φ × Ia ∝ Ia²
```

### Parametry Symulacji
- **J** - Moment bezwładności (0.05 - 0.1 kg·m²)
- **B** - Współczynnik tarcia (0.01 - 0.02)
- **La, Lf** - Indukcyjności (0.1 - 0.3 H)
- **Kt** - Stała momentu (obliczana z danych)

### Metody Numeryczne

#### RK45 (Runge-Kutta 4-5 rzędu)
```javascript
k1 = f(t, y)
k2 = f(t + h/2, y + h×k1/2)
k3 = f(t + h/2, y + h×k2/2)
k4 = f(t + h, y + h×k3)
y_next = y + h×(k1 + 2×k2 + 2×k3 + k4)/6
```

#### Euler (Metoda Eulera)
```javascript
y_next = y + h × f(t, y)
```

---

## 🎨 Funkcje UI

### Responsywność
- **Desktop** (>1200px): Układ dwukolumnowy
- **Tablet** (768-1200px): Układ jednkolumnowy
- **Mobile** (<768px): Zoptymalizowany widok mobilny

### Interaktywne Wykresy (Plotly)
- **Zoom** - Przewiń kółkiem myszy
- **Pan** - Przeciągnij myszą
- **Hover** - Najechanie pokazuje wartości
- **Reset** - Podwójne kliknięcie
- **Download** - Ikona aparatu (zapisz PNG)

### Kolory i Styling
- **Gradient fioletowy** - Nagłówek i przyciski
- **Highlight niebieski** (#667eea) - Ważne wyniki
- **Zielony** (#27ae60) - Punkt początkowy
- **Czerwony** (#e74c3c) - Punkt docelowy
- **Różowy** (#e91e63) - Moment obrotowy
- **Cyjan** (#00bcd4) - Charakterystyki

---

## 📱 Kompatybilność

### Przeglądarki
✅ Chrome 90+
✅ Firefox 88+
✅ Edge 90+
✅ Safari 14+
✅ Opera 76+

### Urządzenia
✅ Desktop (Windows, Mac, Linux)
✅ Tablet (iPad, Android)
✅ Mobile (iPhone, Android)

---

## 🔧 Struktura Pliku

```
dc_motor_simulator.html (pojedynczy plik!)
├── HTML - Struktura strony
├── CSS - Stylowanie i responsywność
└── JavaScript
    ├── ODESolver class (RK45 & Euler)
    ├── calculateShuntMotor()
    ├── calculateSeriesMotorSpeed()
    ├── calculateSeriesMotorTorque()
    ├── plotShuntMotorGraphs()
    ├── plotSeriesMotorSpeedGraphs()
    └── plotSeriesMotorTorqueGraphs()
```

### Zależności Zewnętrzne
- **Plotly.js** v2.27.0 (CDN)
  - `https://cdn.plot.ly/plotly-2.27.0.min.js`

---

## 📊 Przykładowe Wyniki

### Problem 1: Silnik Bocznikowy
```
Moment: 86.77 N·m
Sprawność: 80.04%
Prędkość: 1042.40 rpm
SEM: 207.13 V
Moc wyjściowa: 8.80 kW
```

### Problem 2: Silnik Szeregowy
```
Przy 80A: 600 rpm
Przy 100A: 471.49 rpm
Stosunek prędkości: 0.786
Stosunek momentów: 1.563
```

### Problem 3: Silnik Szeregowy
```
Początkowa: 800 rpm przy 100A
Przy połowie momentu: 1163.96 rpm przy 70.71A
Wzrost prędkości: 45.50%
Redukcja prądu: 29.29%
```

---

## 🎓 Zastosowania Edukacyjne

### Dla Studentów
- Wizualizacja zachowania silników DC
- Zrozumienie charakterystyk prędkość-moment
- Nauka solverów ODE
- Analiza przejściowa i stan ustalony

### Dla Wykładowców
- Interaktywne demo podczas wykładów
- Zadania laboratoryjne
- Porównanie różnych metod numerycznych
- Analiza wpływu parametrów

### Dla Inżynierów
- Szybkie obliczenia projektowe
- Analiza "what-if"
- Weryfikacja obliczeń ręcznych
- Dokumentacja wyników

---

## 🚀 Rozszerzenia i Modyfikacje

### Jak Dodać Nowy Problem
1. Dodaj nową zakładkę w HTML
2. Stwórz funkcję obliczeniową
3. Zaimplementuj wykres
4. Zsynchronizuj suwaki

### Jak Zmienić Parametry Domyślne
```javascript
// W sekcji HTML, zmień wartość "value"
<input type="range" ... value="230">
<input type="number" ... value="230">
```

### Jak Dodać Nowy Solver
```javascript
class ODESolver {
    static mojSolver(f, y0, t0, tf, n) {
        // Twoja implementacja
        return { t, y };
    }
}
```

---

## 📝 Wzory Matematyczne

### Silnik Bocznikowy

**Prąd wzbudzenia:**
```
If = V / Rf
```

**Prąd twornika:**
```
Ia = I - If
```

**Siła elektromotoryczna (SEM):**
```
Eb = V - Ia × Ra
```

**Prędkość:**
```
N = N0 × (Eb / Eb0)
```

**Moment:**
```
T = (Eb × Ia) / ω
gdzie ω = 2π × N / 60
```

**Sprawność:**
```
η = (P_wyjściowa / P_wejściowa) × 100%
```

### Silnik Szeregowy

**SEM:**
```
Eb = V - I(Ra + Rf) - Vb
```

**Prędkość (dla dwóch punktów):**
```
N2/N1 = (Eb2/Eb1) × (I1/I2)
```

**Moment:**
```
T ∝ φ × I ∝ I²
T2/T1 = (I2/I1)²
```

---

## 🐛 Rozwiązywanie Problemów

### Wykresy się nie pokazują
- Sprawdź połączenie internetowe (Plotly z CDN)
- Otwórz konsolę przeglądarki (F12)
- Upewnij się że JavaScript jest włączony

### Wartości są dziwne
- Sprawdź zakresy parametrów
- Zresetuj do wartości domyślnych
- Odśwież stronę (F5)

### Symulacja jest wolna
- Użyj metody Euler zamiast RK45
- Zmniejsz czas symulacji
- Zamknij inne zakładki przeglądarki

---

## 📄 Licencja

MIT License - Wolne do użytku edukacyjnego i komercyjnego

---

## 👨‍💻 Autor

Stworzono dla zaawansowanej analizy maszyn elektrycznych
Wersja: 2.0 (HTML/JavaScript)
Data: 2025

---

## 🌟 Funkcje Premium

### Już Zaimplementowane
✅ Dynamiczna symulacja ODE
✅ Dwa solvery (RK45, Euler)
✅ Interaktywne wykresy Plotly
✅ Responsywny design
✅ Synchronizacja suwaki-input
✅ Wyświetlanie wyników w czasie rzeczywistym
✅ Charakterystyki silników
✅ Stan przejściowy i ustalony

### Możliwe Rozszerzenia
- 💾 Eksport danych do CSV/Excel
- 📊 Porównanie różnych konfiguracji
- 🎨 Tryb ciemny
- 🌍 Wielojęzyczność
- 💻 Tryb offline (PWA)
- 📱 Natywna aplikacja mobilna
- 🔊 Animacje dźwiękowe
- 📈 Zaawansowane wykresy 3D

---

**Ciesz się symulacją! ⚡🔌🔋**
