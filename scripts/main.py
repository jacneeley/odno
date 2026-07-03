'''Main'''
from view.views import ui_driver

def app() -> None:
    '''
        driver code for the application.
    '''
    try:
        if not ui_driver():
            print("Exiting.")
        else:
            print("Complete!")
    except KeyboardInterrupt:
        print("\nQuit.")

if __name__ == "__main__":
    app()
