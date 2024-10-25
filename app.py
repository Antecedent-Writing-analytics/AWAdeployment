from services.configure import ConfigAntecedent 

def main():
    print(f"Step one of Config")
    config = ConfigAntecedent()
    config.configure()


if __name__ == "__main__":
    main()