# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

# from typing import Any, Text, Dict, List

# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher


# class ActionHelloWorld(Action):

#     def name(self) -> Text:
#         return "action_hello_world"

#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

#         dispatcher.utter_message(text="Hello World!")

#         return []


from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import http.client
import json

class ActionGetBookRecommendations(Action):
    def name(self) -> Text:
        return "action_fetch_book_recommendations"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        book_genre = tracker.get_slot("book_genre")  
        if not book_genre:
            dispatcher.utter_message("I couldn't find a book genre.")
            return []
        
        # Debug: Log the extracted book genre
        print(f"Extracted book genre: {book_genre}")

        conn = http.client.HTTPSConnection("book-information-library.p.rapidapi.com")
        headers = {
            'x-rapidapi-key': '11e918100dmsh5fff161f921cd48p135f7djsne23aa7164eed',
            'x-rapidapi-host': 'book-information-library.p.rapidapi.com'
        }
        
        endpoint = f"/api/books/book-recommendations?genre={book_genre}"
        
        try:
            conn.request("GET", endpoint, headers=headers)
            res = conn.getresponse()
            data = res.read().decode("utf-8")
            response_data = json.loads(data)
            
            if res.status == 200 and response_data:
                # Assuming the response contains a list of book recommendations
                book_list = response_data.get('recommendations', [])
                
                if not book_list:
                    dispatcher.utter_message("Sorry, I couldn't find any book recommendations for that genre.")
                    return []
                
                # Format the response message
                message = f"Here are some recommended books for the genre '{book_genre}':\n\n"
                for book in book_list:
                    book_title = book.get('title', 'N/A')
                    book_author = book.get('author', 'Unknown Author')
                    book_summary = book.get('summary', 'No description available.')
                    book_image = book.get('img_url', '')

                    # Append book details to message
                    message += f"**Title**: {book_title}\n"
                    message += f"**Author**: {book_author}\n"
                    message += f"**Summary**: {book_summary}\n"
                    if book_image:
                        message += f"![Book Image]({book_image})\n"
                    message += "\n"

                # Dispatch the message back to the user
                dispatcher.utter_message(text=message)
            
            else:
                dispatcher.utter_message("Sorry, I couldn't fetch book recommendations at the moment.")
        
        except Exception as e:
            # Handle exceptions (e.g., API not responding)
            dispatcher.utter_message("Sorry, I couldn't fetch book recommendations at the moment.")
            print(e)
        
        return []
