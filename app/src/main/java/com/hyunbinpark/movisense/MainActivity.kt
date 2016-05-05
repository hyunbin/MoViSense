package com.hyunbinpark.movisense

import android.hardware.Sensor
import android.hardware.SensorManager
import android.os.Bundle
import android.support.v7.app.AppCompatActivity
import android.util.Log
import com.github.pwittchen.reactivesensors.library.ReactiveSensorFilter
import com.github.pwittchen.reactivesensors.library.ReactiveSensors
import kotlinx.android.synthetic.main.activity_main.*
import org.jetbrains.anko.onClick
import rx.Subscription
import rx.android.schedulers.AndroidSchedulers
import rx.schedulers.Schedulers
import java.util.*
import java.util.concurrent.TimeUnit

class MainActivity : AppCompatActivity() {

  val tag = "MainActivity"

  private var userSetToRun: Boolean = false
  private var accelSubscription: Subscription? = null
  private var gyroSubscription: Subscription? = null
  private var alphabet: ArrayList<Char> = ArrayList()

  private var orientation: Float = 0.0f
  private val gyroThreshold: Float = 10.0f

  private var accelData: MutableList<Float> = ArrayList()
  private val LOWPASS_ALPHA = 0.038f

  override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    setContentView(R.layout.activity_main)

    startButton.onClick { userSetToRun = true; startCollection() }
    endButton.onClick{ userSetToRun = false; stopCollection() }
  }

  override fun onResume(){
    super.onResume()
    if(userSetToRun)
      startCollection()
  }

  override fun onPause(){
    super.onPause()
    if(userSetToRun)
      stopCollection()
  }

  private fun addMotionLetter(c: Char){
    alphabet.add(c)
    motionLabel.text = "" + c
  }

  private fun appendToList(data: MutableList<Float>, input: List<Float>): Boolean {
    var detectedStep: Boolean = false
    for(i in input.indices){
      if(data.size == 0){
        data.add(0.0f)
        continue
      }
      data.add(data.last() + LOWPASS_ALPHA * (input[i] - data.last()))
      Log.d(tag, "Added data point: " + data.last())
      if((data[data.size - 2] > 0 && data[data.size - 1] < 0)
          || (data[data.size - 2] < 0 && data[data.size - 1] > 0)){
        detectedStep = true
      }
    }
    return detectedStep
  }

  private fun startCollection(){
    accelSubscription = ReactiveSensors(this)
        .observeSensor(Sensor.TYPE_ACCELEROMETER, SensorManager.SENSOR_DELAY_FASTEST)
        .subscribeOn(Schedulers.computation())
        .filter(ReactiveSensorFilter.filterSensorChanged())
        .map({x -> x.sensorEvent.values[1]}) // Take only up/down motion
        .buffer(1000, TimeUnit.MILLISECONDS)
        .observeOn(AndroidSchedulers.mainThread())
        .subscribe { x ->
          // Calculate zero crossing for 1 second data set (x)
          val detectedMotion = appendToList(accelData, x)
          if(detectedMotion){
            Log.d(tag, "Detected motion")
            val absoluteOrientation = Math.abs(orientation)
            if(absoluteOrientation >= 0.0f && absoluteOrientation <= 60.0f)
              addMotionLetter('f')
            else if(absoluteOrientation >= 150.0f && absoluteOrientation <= 210.0f)
              addMotionLetter('r')
          }
          else{
            Log.d(tag, "No motion")
            addMotionLetter('s')
          }
        }

    gyroSubscription = ReactiveSensors(this)
        .observeSensor(Sensor.TYPE_GYROSCOPE, SensorManager.SENSOR_DELAY_FASTEST)
        .subscribeOn(Schedulers.computation())
        .filter(ReactiveSensorFilter.filterSensorChanged())
        .map({x -> x.sensorEvent.values[2]}) // Take only rotation in user axis
        .map({x -> Math.toDegrees(x.toDouble()).toFloat()}) // Convert to degrees
        .buffer(1000, TimeUnit.MILLISECONDS) // Emit event every one second
        .map(fun (x: List<Float>): Float{ // Take sum of buffer
          var sum = 0.0f
          val dT = 1.0f / x.size
          for(num in x){
            sum += num * dT
          }
          return sum
        })
        .observeOn(AndroidSchedulers.mainThread())
        .subscribe { x ->
          // Manipulate gyro displacement for 1 second data set (x)
          if(Math.abs(x) >= gyroThreshold) orientation += x
          Log.d(tag, "Current orientation: " + orientation)
        }
  }

  private fun stopCollection(){
    accelSubscription?.unsubscribe()
    gyroSubscription?.unsubscribe()
    orientation = 0.0f
    accelData.clear()
    motionLabel.text = "--"
  }
}
