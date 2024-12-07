from tg import Operator, Session

session = Session()
operator = Operator(id=843805273, username="operator_username")  # Замените ID на Telegram ID оператора
session.add(operator)
session.commit()
session.close()