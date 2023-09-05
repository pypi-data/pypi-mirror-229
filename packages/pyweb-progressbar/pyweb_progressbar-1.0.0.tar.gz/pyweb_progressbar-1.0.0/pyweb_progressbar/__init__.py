import time, sys

class progressBar:
    def __init__(self, base_amount: int, progressBarSize: int = 100, lang: str = 'ru') -> None:
        """
            lang = 'ru' | 'eng'
        """
        self.base_amount = base_amount
        self.size = progressBarSize
        self.start_time = time.time()
        self.lang = lang
        
        end_time = time.time()
        execution_time = end_time - self.start_time
        
        hours = int(execution_time // 3600)
        minutes = int((execution_time % 3600) // 60)
        seconds = int(execution_time % 60)
        
        percent = 0
        progress_bar = ''.join(['_' for _ in range(progressBarSize)])
        sys.stdout.write(f'[{progress_bar}] | {percent:.2f}% | {0} / {base_amount} | {hours:02d}:{minutes:02d}:{seconds:02d}')
        sys.stdout.flush()
        sys.stdout.write('\r')
    
    def updateProgressBar(self, completed_amount: int):
        end_time = time.time()
        execution_time = end_time - self.start_time
        hours = int(execution_time // 3600)
        minutes = int((execution_time % 3600) // 60)
        seconds = int(execution_time % 60)
        
        percent = (completed_amount / self.base_amount) * 100
        completed_width = int(self.size * (completed_amount / self.base_amount))
        progress_bar = ''.join(['█' for _ in range(completed_width)]) + ''.join(['_' for _ in range(self.size - completed_width)])
        sys.stdout.write(f'[{progress_bar}] | {percent:.2f}% | {completed_amount} / {self.base_amount} | {hours:02d}:{minutes:02d}:{seconds:02d}')
        sys.stdout.flush()
        sys.stdout.write('\r')
    
    def end(self):
        end_time = time.time()
        execution_time = end_time - self.start_time
        hours = int(execution_time // 3600)
        minutes = int((execution_time % 3600) // 60)
        seconds = int(execution_time % 60)
        sys.stdout.write('\n')
        sys.stdout.write(f'Выполнение завершено за {hours:02d}:{minutes:02d}:{seconds:02d}' if self.lang == 'ru' else f'Execution completed in {hours:02d}:{minutes:02d}:{seconds:02d}' if self.lang == 'en' else f'{hours:02d}:{minutes:02d}:{seconds:02d}')
        sys.stdout.write('\n')