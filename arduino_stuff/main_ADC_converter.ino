const int pulse_sens = A0; // the piezo is connected to analog pin 0
const int measures_per_sec = 50;
const int seconds_to_estimate = 5;
const int pulsemeasures = measures_per_sec*seconds_to_estimate;
const int max_heart_rate_per_sec = 3.35;
const double delayint = 1000/measures_per_sec;

double pulselvl;
double ppm;

double measure_arr[pulsemeasures];
int counter = 0;

void setup() {
  Serial.begin(9600);       // use the serial port
}

void loop() {
  // read the sensor and store it in the variable sensorReading:
  pulselvl = analogRead(pulse_sens);
  if(counter < pulsemeasures){
    measure_arr[counter] = pulselvl;
    counter++;
  }
  else{
    bool indices_processed[pulsemeasures];
    for (int i = 0; i<pulsemeasures; i++){
      indices_processed[i] = 0;
    }
    int sorted_indices[pulsemeasures];
    double sorted_values[pulsemeasures];
    int highestindex = 0;
    double highest = measure_arr[highestindex];
    double sum = 0;
    double avg = 0;
    int avgcnt = 0;
    for (int qavg = 3; qavg>0; qavg--){
      for (int i = 0; i<pulsemeasures; i++){
        //Serial.println(measure_arr[i]);
        if(measure_arr[i]>avg){
        sum += measure_arr[i];
        avgcnt++;
        }
      }
      avg = sum/avgcnt;
    }
    
    
//    for (int j = 0; j<pulsemeasures; j++){
//      for(int i = 0; i<pulsemeasures; i++){
//        if(measure_arr[i] >= highest && !indices_processed[i]){
//          highestindex = i;
//          highest = measure_arr[highestindex];
//        }
//      }
//      indices_processed[highestindex] = 1;
//      sorted_indices[j] = highestindex;
//      sorted_values[j] = highest;
//      highest = 0;
    //ppm = bangs*60/seconds_to_estimate;
    //Serial.println(ppm);
    //}

   int bangs[pulsemeasures/4];
   bool up = 0;
   int cnt = 0;
   for(int i = 0; i<pulsemeasures; i++){
    if(measure_arr[i]>avg && !up) up = 1;
    if(measure_arr[i]<avg && up) {
      bangs[cnt] = i;
      up = 0;
      cnt++;
    }
   }
   double bangtimesum = 0;
   for(int i = 1; i<cnt; i++){
      bangtimesum += bangs[i]-bangs[i-1];
   }
   
   ppm =  60000/((bangtimesum/cnt)*delayint);
   counter = 0;
   //Serial.println(ppm);

  }
//  Serial.println("Tense:");
//  Serial.println(pulselvl);
//  Serial.println("Measured:");
  Serial.println(ppm);
  delay(delayint);  // delay to avoid overloading the serial port buffer
}

