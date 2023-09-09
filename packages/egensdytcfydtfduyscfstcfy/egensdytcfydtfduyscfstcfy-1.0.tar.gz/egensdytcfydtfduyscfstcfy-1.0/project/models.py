class User:
    """ 
    Клас користувача для входу у систему

    :param login: Параметр логіну користувача
    :type login: str
    :param password: Параметр паролю користувача користувача
    :type password: str
    """
    def __init__(self,
                 login:str,
                 password:str):
        """
        Дія ініціалізації об'єкту
        """
        self.__login
        self.__password

    
    def check_login(self,
                    login:str,
                    password:str):
        """
        Метод перевірки логіну і паролю на відповідність користувачу

        :param login: Параметр логіну користувача
        :type login: str
        :param password: Параметр паролю користувача користувача
        :type password: str
        :return: True якщо параметри відповідають користувачу false якщо не відповідають
        :rtype: bool
        """
        if self.__login == login and self.__password == password:
            return True
        else:
            return False
