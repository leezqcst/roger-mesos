import utils
import re

class FileAuthorizer:
    class __FileAuthorizer:

        def __init__(self, filename):
            self.filename = filename
            self.data = utils.parse_permissions_file(filename)

        def get_merged_data(self, user, allowed_users, allowed_actions, data, action):
            if user in allowed_users:
                return
            allowed_users.append(user)
            if action != '':
                if action in data[user]['action'].keys():
                    temp_list = list(set(data[user]['action'][action]) - set(allowed_actions))
                    for item in temp_list:
                        allowed_actions.append(item)            

            if 'can_act_as' not in data[user]:
                return

            for u in data[user]['can_act_as']:
                self.get_merged_data(u, allowed_users, allowed_actions, data, action)

        def resource_check(self, resource, allowed_actions):
            for pattern in allowed_actions:
                prog = re.compile(pattern)
                result = prog.match(resource)
                if result:
                    return True

            return False

        def authorize(self, user, act_as, resource, action = "GET"):
            if not user or not act_as or not resource:
                return False

            if user not in self.data.keys() or act_as not in self.data.keys():
                print "User [{}] or act as user [{}] is not an authorized user".format(user, act_as)
                return False            

            if user != act_as:
                if 'can_act_as' not in self.data[user]:
                    print "Authorization Failed: {} cannot act as {}".format(user, act_as)
                    return False

            allowed_users_list = []
            self.get_merged_data(user, allowed_users_list, [], self.data, '')

            if act_as not in allowed_users_list:
                print "Authorization Failed: {} cannot act as {}".format(user, act_as)
                return False

            allowed_users_list = []
            allowed_actions = self.data[act_as]['action'][action]
            self.get_merged_data(act_as, allowed_users_list, allowed_actions, self.data, action)
         
            result = self.resource_check(resource, allowed_actions)
            if result == False:
                print "User [{}] acting as [{}] is not authorized for requested resource [{}]".format(user, act_as, resource)
                return False

            return True

    instance = None
    def __init__(self, filename):
        if not FileAuthorizer.instance:
            FileAuthorizer.instance = FileAuthorizer.__FileAuthorizer(filename)
        else:
            FileAuthorizer.instance.filename = filename
