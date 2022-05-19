from DetectorML import HandObject

one_finger_poses = ['thumbsUp', 'pointer', 'middleFinger', 'ringFinger', 'pinky']


def count_fingers(event: HandObject):
    return [f.isUp for f in event.fingers].count(True)


def areUp(event: HandObject, fingers):
    return all([event.fingers[i].isUp for i in fingers])


def classify(event: HandObject):

    fn = count_fingers(event)

    if fn == 0:
        return 'closed'

    if fn == 1:
        index = [f.isUp for f in event.fingers].index(True)
        return one_finger_poses[index]

    if fn == 2:
        if areUp(event, (1,2)):
            return 'peaceSign'
        if areUp(event, (0,1)):
            return 'check'
        if areUp(event, (0,4)):
            return 'wide'
        if areUp(event, (1,4)):
            return 'rock'
        return None

    if fn == 3:
        if areUp(event, (1,2,3)):
            return 'middleThree'
        if areUp(event, (2,3,4)):
            return 'lastThree'
        if areUp(event, (1,3,4)):
            return '134'
        if areUp(event, (0,1,4)):
            return 'spiderman'
        return None

    if fn == 4:
        if areUp(event, (1,2,3,4)):
            return 'normalFour'
        return None

    if fn == 5:
        return 'opened'
