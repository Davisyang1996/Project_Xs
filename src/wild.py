import rngtool
import cv2
import time
import json
from xorshift import Xorshift

config = json.load(open("config.json"))

def expr():
    player_eye = cv2.imread(config["image"], cv2.IMREAD_GRAYSCALE)
    if player_eye is None:
        print("path is wrong")
        return
    blinks, intervals, offset_time = rngtool.tracking_blink(player_eye, *config["view"], sysdvr=config["SysDVR"])
    prng = rngtool.recov(blinks, intervals)

    waituntil = time.perf_counter()
    diff = round(waituntil-offset_time)
    prng.getNextRandSequence(diff)

    state = prng.getState()
    print(hex(state[0]<<32|state[1]), hex(state[2]<<32|state[3]))

    advances = 0

    for _ in range(1000):
        advances += 1
        r = prng.next()
        waituntil += 1.018

        print(f"advances:{advances}, blinks:{hex(r&0xF)}")        
        
        next_time = waituntil - time.perf_counter() or 0
        time.sleep(next_time)

def firstspecify():
    player_eye = cv2.imread("./trainer/ruins/eye.png", cv2.IMREAD_GRAYSCALE)
    if player_eye is None:
        print("path is wrong")
        return
    blinks, intervals, offset_time = rngtool.tracking_blink(player_eye, 910, 485, 50, 60)
    prng = rngtool.recov(blinks, intervals)

    waituntil = time.perf_counter()
    diff = round(waituntil-offset_time)
    prng.getNextRandSequence(diff)

    state = prng.getState()
    print("state(64bit 64bit)")
    print(hex(state[0]<<32|state[1]), hex(state[2]<<32|state[3]))
    print("state(32bit 32bit 32bit 32bit)")
    print(*[hex(s) for s in state])

def reidentify():
    print("input xorshift state(state[0] state[1] state[2] state[3])")
    state = [int(x,0) for x in input().split()]

    player_eye = cv2.imread("./trainer/ruins/eye.png", cv2.IMREAD_GRAYSCALE)
    if player_eye is None:
        print("path is wrong")
        return

    observed_blinks, _, offset_time = rngtool.tracking_blink(player_eye, 910, 485, 50, 60,size=20)
    reidentified_rng = rngtool.reidentifyByBlinks(Xorshift(*state), observed_blinks)
    
    waituntil = time.perf_counter()
    diff = round(waituntil-offset_time)+1
    reidentified_rng.getNextRandSequence(diff)

    state = reidentified_rng.getState()
    print("state(64bit 64bit)")
    print(hex(state[0]<<32|state[1]), hex(state[2]<<32|state[3]))
    print("state(32bit 32bit 32bit 32bit)")
    print(*[hex(s) for s in state])

    #timecounter reset
    advances = 0
    wild_prng = Xorshift(*reidentified_rng.getState())
    isUnown = True
    wild_prng.getNextRandSequence(2+isUnown)

    advances = 0

    while True:
        advances += 1
        r = reidentified_rng.next()
        wild_r = wild_prng.next()

        waituntil += 1.018

        print(f"advances:{advances}, blinks:{hex(r&0xF)}")        
        
        next_time = waituntil - time.perf_counter() or 0
        time.sleep(next_time)

if __name__ == "__main__":
    expr()