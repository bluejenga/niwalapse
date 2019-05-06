#!/usr/bin/env python3

import schedule
import time
import job

#TIME_TO_SHUTTER = "10:14"
TIME_TO_SHUTTER = "10:00"

schedule.every().day.at(TIME_TO_SHUTTER).do(job.job)

while True:
	schedule.run_pending()
	time.sleep(1)
