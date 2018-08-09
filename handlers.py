import os
import re
import time
import datetime
from logging.handlers import TimedRotatingFileHandler


class KylejanTimedRotatingFileHandler(TimedRotatingFileHandler):
    def __init__(self, path, name, when='midnight', interval=1):
        if not os.path.exists(path):
            os.makedirs(path)
        self.static_file_name = name
        self.prefix = '%Y-%m-%d_%H_%M_%S'
        filename = '{}/{}--{}'.format(path, datetime.datetime.now().strftime(self.prefix), name)
        TimedRotatingFileHandler.__init__(self, filename,
            when=when,
            interval=interval,
            encoding='utf8')

    def getFilesToDelete(self):
        """
        Determine the files to delete when rolling over.
        More specific than the earlier method, which just used glob.glob().
        """
        dirName, _ = os.path.split(self.baseFilename)
        fileNames = os.listdir(dirName)
        result = []

        extMatch = r"^\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}(\.\w+)?$"
        extMatch = re.compile(extMatch, re.ASCII)

        for fileName in fileNames:
            suffix = fileName.split('--')[-1]
            if suffix == self.static_file_name:
                prefix = fileName.split('--')[0].split('/')[-1]
                if extMatch.match(prefix):
                    result.append(os.path.join(dirName, fileName))
        if len(result) < self.backupCount:
            result = []
        else:
            result.sort()
            result = result[:len(result) - self.backupCount]
        return result

    def doRollover(self):
        """
        do a rollover; in this case, a date/time stamp is appended to the filename
        when the rollover happens.  However, you want the file to be named for the
        start of the interval, not the current time.  If there is a backup count,
        then we have to get a list of matching filenames, sort them and remove
        the one with the oldest suffix.
        """
        if self.stream:
            self.stream.close()
            self.stream = None
        # get the time that this sequence started at and make it a TimeTuple
        currentTime = int(time.time())
        dstNow = time.localtime(currentTime)[-1]
        t = self.rolloverAt - self.interval
        if self.utc:
            timeTuple = time.gmtime(t)
        else:
            timeTuple = time.localtime(t)
            dstThen = timeTuple[-1]
            if dstNow != dstThen:
                if dstNow:
                    addend = 3600
                else:
                    addend = -3600
                timeTuple = time.localtime(t + addend)

        dir_name, _ = os.path.split(self.baseFilename)
        dfn = self.rotation_filename('{}/{}--{}'.format(dir_name, time.strftime(self.prefix, timeTuple), self.static_file_name))
        if os.path.exists(dfn):
            os.remove(dfn)
        self.rotate(self.baseFilename, dfn)
        if self.backupCount > 0:
            for s in self.getFilesToDelete():
                os.remove(s)
        if not self.delay:
            self.stream = self._open()
        newRolloverAt = self.computeRollover(currentTime)
        while newRolloverAt <= currentTime:
            newRolloverAt = newRolloverAt + self.interval
        #If DST changes and midnight or weekly rollover, adjust for this.
        if (self.when == 'MIDNIGHT' or self.when.startswith('W')) and not self.utc:
            dstAtRollover = time.localtime(newRolloverAt)[-1]
            if dstNow != dstAtRollover:
                if not dstNow:  # DST kicks in before next rollover, so we need to deduct an hour
                    addend = -3600
                else:           # DST bows out before next rollover, so we need to add an hour
                    addend = 3600
                newRolloverAt += addend
        self.rolloverAt = newRolloverAt