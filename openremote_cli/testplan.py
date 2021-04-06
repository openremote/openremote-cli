import argparse
import sys

# TODO move test covered by testplan to this file. Example:
# def manager_test_http_rest(delay=1, quit=True):
#     if not hasattr(config, 'DRY_RUN'):
#         # When running directly from installed scripts
#         config.initialize()
#         parser = argparse.ArgumentParser(
#             description=f'Test plan HTTP REST',
#             formatter_class=argparse.ArgumentDefaultsHelpFormatter,
#         )
#         parser.add_argument(
#             '-d',
#             '--dnsname',
#             type=str,
#             required=False,
#             help='OpenRemote dns',
#             default='staging.demo.openremote.io',
#         )
#         parser.add_argument(
#             '-u',
#             '--user',
#             type=str,
#             required=False,
#             help='username',
#             default='admin',
#         )
#         parser.add_argument(
#             '--delay',
#             type=int,
#             help='delay between steps in test scenarios',
#             default=1,
#         )
#         parser.add_argument(
#             '--no-quit', action='store_true', help='open browser and login'
#         )
#         args = parser.parse_args(sys.argv[1:])
#         url = args.dnsname
#         user = args.user
#         delay = args.delay
#         quit = not args.no_quit
#     else:
#         url = 'staging.demo.openremote.io'
#         user = 'admin'
#     print(f"0. Login into {url}")
#     driver = _manager_ui_login(url, user, realm='master')
#     _manager_ui_wait_map(driver, url)
#     # test plan https://docs.google.com/document/d/1RVt47Y9KLJl_YSNwoLrOE3VNWfUm2VaOpZzS7tebItI/edit
#     print("1. Go to the 'Assets' page in the webapp")
#     time.sleep(delay)
#     driver.go_to(f'https://{url}/manager/#!assets')
#     print(
#         "2. Open the add asset dialog by clicking the '+' icon in the asset tree on the left."
#     )
#     time.sleep(delay)
#     _manager_ui_add_asset_dialog(driver, url)
#     print("3. Give the asset the name 'Weather Agent'")
#     time.sleep(delay)
#     _manager_ui_add_http_weather_agent(driver, url)
#     print("4. and select the asset type 'HTTP Client Agent' from the list.")
#     time.sleep(delay)
#     _manager_ui_select_http_agent(driver, url)
#     print("5. Press 'Add'")
#     time.sleep(delay)
#     _manager_ui_press_add(driver, url)
#     print(
#         "6. First we set the Base URI of the weather service that we will use for further queries. TODO"
#     )
#     if quit:
#         # Need this for manager to act (maybe some confirmation TODO)
#         time.sleep(1)
#     else:
#         input('Press ENTER to quit')
