from photobook.core import Image
from photobook.scripts.populateImageAttributes import getImageAttributes
from tqdm import tqdm
import sys, os, shutil
from datetime import datetime
import logging

if __name__=="__main__":

    fileHandler = logging.FileHandler("sortImages.log")
    streamHandler = logging.StreamHandler(sys.stdout)

    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        handlers = [fileHandler]) #, streamHandler])
    logger = logging.getLogger("sortImages")

    EXTENSIONS = (".jpg", ".jpeg", ".tif", ".tiff", ".png", ".heic")

    try:
        inputDir = sys.argv[1]
        outputDir = sys.argv[2]
        dryRun = False

        outputDirUnknownDate = os.path.join(outputDir, "unknownDate")
        outputDirUnknownFormat = os.path.join(outputDir, "unknownFormat")
        outputDirErrors = os.path.join(outputDir, "errors")

        numFiles = 0
        for dn,dns,fns in os.walk(inputDir):
            numFiles += len(fns)

        pb = tqdm(desc="Sorting Images", total=numFiles)

        for idir,dirnames,filenames in os.walk(inputDir):
            for fn in filenames:
                ipath = os.path.join(idir, fn)

                try:
                    if os.path.splitext(fn)[1].lower() in EXTENSIONS:
                        dt = getImageAttributes(ipath)[4]
                        if dt is None:
                            logger.info(f"unable to obtain date for: {ipath}, moving to 'unknown date' directory")
                            # dt = datetime.fromtimestamp(os.stat(ipath).st_mtime)
                            odir = outputDirUnknownDate
                        else:
                            odir = os.path.join(outputDir, f"{dt.year}", f"{dt.month:02d}", f"{dt.day:02d}")
                    else:
                        logger.info(f"Unrecognized file format: {ipath}, moving to 'unknown format' directory")
                        odir = outputDirUnknownFormat

                except Exception as e:
                    logger.critical(f"Exception handling: {ipath}, moving to 'errors' directory")
                    logger.critical(e, exc_info=True)
                    odir = outputDirErrors

                opath = os.path.join(odir, fn)

                if os.path.exists(opath):
                    # output exists, verify size is the same
                    istat = os.stat(ipath)
                    ostat = os.stat(opath)
                    if istat.st_size == ostat.st_size:
                        logger.info(f"skipping, files are same size: {ipath}, {opath}")
                    else:
                        logger.info(f"copying, {ipath} size ({istat.st_size}) differs from {opath} ({ostat.st_size})")
                        if not dryRun:
                            shutil.copy2(ipath, opath)
                else:
                    logger.debug(f"{ipath} -> {opath}")
                    if not dryRun:
                        os.makedirs(odir, exist_ok=True)
                        shutil.copy2(ipath, opath)

                pb.update()

    except Exception as e:
        logger.critical(e, exc_info=True)
        raise e
