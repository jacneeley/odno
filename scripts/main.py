'''Main'''
from view.views import ui_driver

def app() -> None:
    '''
        driver code for the application.
    '''
    try:
        if ui_driver():
            print("Complete!")

        else:
            print("Exiting.")

    except KeyboardInterrupt:
        print("\nQuit.")

if __name__ == "__main__":
    app()
