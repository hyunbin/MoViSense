package com.hyunbinpark.movisense

import android.hardware.Sensor
import android.os.Bundle
import android.support.v7.app.AppCompatActivity
import android.util.Log
import com.github.pwittchen.reactivesensors.library.ReactiveSensorFilter
import com.github.pwittchen.reactivesensors.library.ReactiveSensors
import kotlinx.android.synthetic.main.activity_main.*
import org.jetbrains.anko.onClick
import org.jetbrains.anko.sensorManager
import rx.Subscription
import rx.android.schedulers.AndroidSchedulers
import rx.schedulers.Schedulers
import java.util.*
import java.util.concurrent.TimeUnit

class MainActivity : AppCompatActivity() {

  val tag = "MainActivity"

  private var subscription: Subscription? = null
  private var userSetToRun: Boolean = false

  private var velocity : Float = 0.0f
  private val THRESHOLD_ACCEL: Float = 1.0f
  private var alphabet: ArrayList<Char> = ArrayList()

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
    subscription = ReactiveSensors(this).observeSensor(Sensor.TYPE_ACCELEROMETER)
        .subscribeOn(Schedulers.computation())
        .filter(ReactiveSensorFilter.filterSensorChanged())
        .map({x -> x.sensorEvent.values[1]})
        .buffer(500, TimeUnit.MILLISECONDS)
        .observeOn(AndroidSchedulers.mainThread())
        .subscribe { x ->
          // Crude integration to calculate velocity
          val period = 1.0f / x.size
          var currentVelocity : Float = 0.0f
          for(number in x){
            Log.d(tag, "Accel: " + number)
            currentVelocity += number * period
          }

          if(Math.abs(currentVelocity) > 0.3f) velocity += currentVelocity

          // Log our results
          val message : String = String.format("Velocity: %f", velocity);
          Log.d(tag, message)

          // Determine which letter to add to list
          if(velocity > THRESHOLD_ACCEL) addToList('m')
          else addToList('n')
        }
  }

  private fun stopCollection(){
    subscription?.unsubscribe()
    velocity = 0.0f
    motionLabel.text = "--"
  }
}
