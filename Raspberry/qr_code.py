import cv2

def readQrCode():
    dataReaded ="Nothing"
    # inizializzazione della camera
    cap = cv2.VideoCapture(0)
    # istanza dell'oggetto rilevatore dei qrCode
    detector = cv2.QRCodeDetector()
    checkData = True

    while checkData:
        # get dell'immagine rilevata dalla camera
        _, img = cap.read()
        # get delle informazioni relative alle coordinate e le informazioni del bounding box 
        data, bbox, _ = detector.detectAndDecode(img)
        # se è rilevata una bounding box, ne evidenzia i contorni, e ne scrive su schermo il contenuto del qrCode
        if(bbox is not None):
            for i in range(len(bbox)):
                cv2.line(img, tuple(bbox[i][0]), tuple(bbox[(i+1) % len(bbox)][0]), color=(255,
                        0, 255), thickness=2)
            cv2.putText(img, data, (int(bbox[0][0][0]), int(bbox[0][0][1]) - 10), cv2.FONT_HERSHEY_SIMPLEX,
                        0.5, (0, 255, 0), 2)
            if data:
                checkdata= False
                dataReaded = data
                break
        # visualizzazione anteprima
        cv2.imshow("code detector", img)
        if(cv2.waitKey(1) == ord("q")| checkData==False):
            break
    # rilascio dell'oggetto e terminazione della rilevazione
    cap.release()
    cv2.destroyAllWindows()
    return dataReaded
