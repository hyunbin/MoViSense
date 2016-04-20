package com.hyunbinpark.movisense

import android.hardware.Sensor
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

  private fun addToList(c: Char){
    alphabet.add(c)
    motionLabel.text = "" + c
  }

  private fun startCollection(){
    accelSubscription = ReactiveSensors(this).observeSensor(Sensor.TYPE_ACCELEROMETER)
        .subscribeOn(Schedulers.computation())
        .filter(ReactiveSensorFilter.filterSensorChanged())
        .map({x -> x.sensorEvent.values[1]})
        .buffer(1000, TimeUnit.MILLISECONDS)
        .observeOn(AndroidSchedulers.mainThread())
        .subscribe { x ->
          // Calculate zero crossing for 1 second data set (x)

        }

    gyroSubscription = ReactiveSensors(this).observeSensor(Sensor.TYPE_GYROSCOPE)
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
    motionLabel.text = "--"
  }
}
