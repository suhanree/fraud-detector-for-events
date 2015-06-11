import json
import os
import sys
import cPickle as pickle

from model import buildmodel, predict
from sklearn.ensemble import RandomForestClassifier

# Filename for the pickle object.
filename_pickle = 'data/model.pkl'

# Our model.
our_model = RandomForestClassifier(n_estimators=100, oob_score=True)

# Features we use from the original dataset.
# They are divided into two groups: category and non-category.
label_name = 'acct_type'
category_features = ['channels', 'country', 'currency', 'delivery_method',
                    'fb_published', 'has_analytics', 'has_header',
                    'has_logo', 'listed', 'payout_type', 'show_map',
                    'user_type', 'venue_country']
non_category_features = ['approx_payout_date', 'body_length', 'num_payouts',
                        'sale_duration', 'sale_duration2',
                        'user_age', 'venue_latitude', 'venue_longitude']

def score(data):
    # Get the prediction
    prediction = predict(data, our_model, final_columns, category_features, averages)

    # save the data and prediction in our db.

    return prediction


if __name__ == '__main__':
    # If the pickle object doesn't exist or the rebuild option
    # is given by the command line.
    if (not os.path.exists(filename_pickle)) or \
        (len(sys.argv) > 1 and sys.argv[1] == 'rebuild'):
        (built_model, final_columns, averages) = buildmodel(label_name, category_features,
                            non_category_features, model=our_model, save=True)
        print "Built the model, and saved as pickle"
    else:
        print "Opening pickle..."
        with open(filename_pickle, 'r') as f:
            (built_model, final_columns, averages) = pickle.load(f)
    our_model = built_model

    data = json.dumps({"org_name": "DREAM Project Foundation", "name_length": 51, "event_end": 1363928400, "venue_latitude": 42.9630578, "event_published": 1361978554.0, "user_type": 1, "channels": 11, "currency": "USD", "org_desc": "", "event_created": 1361291193, "event_start": 1363914000, "has_logo": 1, "email_domain": "dreamprojectfoundation.org", "user_created": 1361290985, "payee_name": "", "payout_type": "ACH", "venue_name": "Grand Rapids Brewing Co", "sale_duration2": 30, "venue_address": "1 Ionia Avenue Southwest", "approx_payout_date": 1364360400, "org_twitter": 13.0, "gts": 537.4, "listed": "y", "ticket_types": [{"event_id": 5558108, "cost": 50.0, "availability": 1, "quantity_total": 125, "quantity_sold": 10}], "org_facebook": 13.0, "num_order": 7, "user_age": 0, "body_length": 1474, "description": "<p><span style=\"font-size: medium; font-family: 'book antiqua', palatino;\">Come enjoy a night of music and beer tasting at the new Grand Rapids Brewery while we make an effort to create awareness and raise funds for Dream Project Foundation. The night will include music, Grand Rapids Brewery's finest beer to sample, heavy hors d'oeuvre's and silent auction of artwork directly from the young artists of Dream House.</span></p>\r\n<p>&nbsp;</p>\r\n<p>Who We Are:</p>\r\n<p>DREAM Project Foundation is a small American 501c3 registered non-profit organization, working to break the cycle of human trafficking through community development. As a small, grass roots organization, we focus primarily on prevention and protection which begins with shelter and continues with education, so those vulnerable are aware of the dangers and able to protect themselves.</p>\r\n<p>DREAM Project Foundation was officially founded in 2011 to support the DREAM House children's home based in Thailand on the border of Myanar (Burma). While helping children stay safe from the trafficing is the heart of our mission, we know that in order to end trafficking it must be a collaborative effort for all people and communities.&nbsp;</p>\r\n<p>We at DREAM Project Foundation are determined to fight against this atrocity, focusing on the factors that cause people to be vulnerable targets to traffickers, with most of our work based in SE Asia as it is a major international hub of human trafficking.</p>", "object_id": 5558108, "venue_longitude": -85.6706147, "venue_country": "US", "previous_payouts": [{"name": "", "created": "2013-04-19 03:25:42", "country": "US", "state": "", "amount": 500.0, "address": "", "zip_code": "", "event": 5558108, "uid": 52778636}], "sale_duration": 22.0, "num_payouts": 0, "name": "DREAM Project Foundation - Taste of a Better Future", "country": "US", "delivery_method": 0.0, "has_analytics": 0, "fb_published": 0, "venue_state": "MI", "has_header": 'null', "show_map": 1})
    #print data
    print 'score', score(json.loads(data))

    with open('data/test_new.json') as f:
        test_data = json.load(f)
    for ddd in test_data:
        print ddd['acct_type'], predict(ddd, our_model, final_columns, category_features, averages)
