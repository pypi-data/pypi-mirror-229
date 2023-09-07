from pathlib import Path

from .SHHSAnnotationLoader import SHHSAnnotationLoader
from pyPhasesRecordloader.recordLoaders.EDFRecordLoader import EDFRecordLoader
from pyPhasesRecordloader.recordLoaders.CSVMetaLoader import CSVMetaLoader


class RecordLoaderSHHS(EDFRecordLoader):
    def __init__(
        self,
        filePath,
        targetSignals,
        targetSignalTypes=[],
        optionalSignals=[],
        combineChannels=[],
    ) -> None:
        super().__init__(
            filePath,
            targetSignals,
            targetSignalTypes=targetSignalTypes,
            optionalSignals=optionalSignals,
            combineChannels=combineChannels,
        )

        self.exportsEventArray = True

    def isVisit1(self, recordName):
        return recordName[:5] == "shhs1"
    
    def getVisit(self, recordName):
        return 1 if self.isVisit1(recordName) else 0
    
    def getFileBasePath(self, recrdId):
        return self.filePath

    def getFilePathSignal(self, recordId):
        visit = self.getVisit(recordId)
        return f"{self.getFileBasePath(recordId)}/polysomnography/edfs/shhs{visit}/{recordId}.edf"

    def getFilePathAnnotation(self, recordId):
        visit = self.getVisit(recordId)
        return f"{self.getFileBasePath(recordId)}/polysomnography/annotations-events-nsrr/shhs{visit}/{recordId}-nsrr.xml"

    def existAnnotation(self, recordId):
        return Path(self.getFilePathAnnotation(recordId)).exists()

    def exist(self, recordId):
        return Path(self.getFilePathAnnotation(recordId)).exists() & Path(self.getFilePathSignal(recordId)).exists()

    def loadAnnotation(self, recordId, fileName, valueMap=None):
        filePath = self.getFilePathAnnotation(recordId)
        annotationLoader = SHHSAnnotationLoader.load(filePath, valueMap, self.annotationFrequency)

        return annotationLoader.events

    def getEventList(self, recordName, targetFrequency=1):
        metaXML = self.getFilePathAnnotation(recordName)
        xmlLoader = SHHSAnnotationLoader()

        eventArray = xmlLoader.loadAnnotation(metaXML)
        self.lightOff = xmlLoader.lightOff
        self.lightOn = xmlLoader.lightOn

        if targetFrequency != 1:
            eventArray = self.updateFrequencyForEventList(eventArray, targetFrequency)

        return eventArray

    def getMetaData(self, recordName):
        metaData = super().getMetaData(recordName)
        metaData["recordId"] = recordName
        relevantRows = {
            "gender": "gender",
            "age_s1": "age",
            "bmi_s1": "bmi",
            # therapy / diagnostics
            "slptime": "tst",
            "slp_lat": "sLatency",
            "rem_lat1": "rLatency",
            "WASO": "waso",
            "slp_eff": "sEfficiency",
            "ai_all": "indexArousal",
            # % N1, N2, N3, R
            # countArousal
            "ArREMBP": "ArREMBP",
            "ArREMOP": "ArREMOP",
            "ArNREMBP": "ArNREMBP",
            "ArNREMOP": "ArNREMOP",
            # PLMSI
            # PLMSIArI
            # AHI
            "ahi_a0h4a": "ahi",
            # Diagnosis
            "DiasBP": "bp_diastolic",
            "SystBP": "bp_systolic",
            "race": "race", 
        }
        # ArREMBP + ArREMOP + ArNREMBP + ArNREMOP
        visit = self.getVisit(recordName)
        csvLoader = CSVMetaLoader(
            f"{self.filePath}/datasets/shhs{visit}-dataset-0.15.0.csv", idColumn="nsrrid", relevantRows=relevantRows
        )
        csvMetaData = csvLoader.getMetaData(int(recordName[6:]))
        metaData.update(csvMetaData)

        metaData["countArousal"] = metaData["ArREMBP"] + metaData["ArREMOP"] + metaData["ArNREMBP"] + metaData["ArNREMOP"]

        return metaData
