#!/usr/bin/env python
import sys
import time
import logging
import boto3
from botocore.exceptions import ClientError
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

logging.basicConfig(level=logging.INFO,format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logging.getLogger('boto3').setLevel(logging.CRITICAL)
logging.getLogger('botocore').setLevel(logging.CRITICAL)

s3 = boto3.client('s3')

S3_DST_BUCKET = "s3-sync-example"


class S3Handler(PatternMatchingEventHandler):
    # patterns = ["*.xml", "*.lxml"]

    def process(self, event):
        """
        event.event_type
            'modified' | 'created' | 'moved' | 'deleted'
        event.is_directory
            True | False
        event.src_path
            path/to/observed/file
        """
        # the file will be processed there
        if event.is_directory == False:
            s3_key = event.src_path.lstrip("./")
            try:
                with open(event.src_path, 'rb') as data:
                    s3.upload_fileobj(data, S3_DST_BUCKET, s3_key)
            except ClientError as e:
                logging.error(e)


    def on_any_event(self, event):
        if event.is_directory == False:
            s3_key = event.src_path.lstrip("./")
            logging.info("[{}] {}".format(event.event_type, s3_key))


    def on_modified(self, event):
        self.process(event)

    def on_created(self, event):
        self.process(event)

    def on_deleted(self, event):
        try:
            s3.delete_object(
                Bucket=S3_DST_BUCKET,
                Key=event.src_path.lstrip("./"),
            )
        except ClientError as e:
            logging.error(e)


if __name__ == "__main__":

    path = sys.argv[1] if len(sys.argv) > 1 else './folder'
    observer = Observer()
    observer.schedule(S3Handler(), path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
