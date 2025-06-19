import threading
import itertools
import sys
import time

class LoadingAnimation:
    def __init__(self, message="⏳ 답변 생성 중"):
        self.done = False
        self.message = message
        self._thread = threading.Thread(target=self.animate)

    def start(self):
        self._thread.start()

    def stop(self):
        self.done = True
        self._thread.join()
        # 💡 기존 줄 지우고 커서 복귀
        sys.stdout.write("\\r" + " " * 80 + "\\r")
        sys.stdout.flush()

    def animate(self):
        for dots in itertools.cycle([".", "..", "...", "....", "....."]):
            if self.done:
                break
            sys.stdout.write(f"\r{self.message}{dots}{' ' * 20}")
            sys.stdout.flush()
            time.sleep(0.5)