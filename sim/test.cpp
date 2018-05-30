#include "channel_simulator.h"
#include "../src/core/options.h"

int main(int argc, char** argv) {
  Options::Parse(argc, argv);
  FILE* sender_config = fopen("/home/njay2/PCC/restructure/sim/sender.config", "r");
 
  double dur = 100;
  if (Options::Get("--sim-dur=") != NULL) {
    dur = atof(Options::Get("--sim-dur="));
  }
  
  double test_bw = 70;
  if (Options::Get("--test-bw=") != NULL) {
    test_bw = atof(Options::Get("--test-bw="));
  }
  
  double test_dl = 0.03;
  if (Options::Get("--test-dl=") != NULL) {
    test_dl = atof(Options::Get("--test-dl="));
  }
  
  double test_buf = 500;
  if (Options::Get("--test-buf=") != NULL) {
    test_buf = atof(Options::Get("--test-buf="));
  }
  
  double test_plr = 0.00;
  if (Options::Get("--test-plr=") != NULL) {
    test_plr = atof(Options::Get("--test-plr="));
  }
  
  std::cout << "bw = " << test_bw << std::endl;
  std::cout << "dl = " << test_dl << std::endl;
  std::cout << "buf = " << test_buf << std::endl;
  std::cout << "plr = " << test_plr << std::endl;
  Simulator simulator = Simulator(sender_config, test_bw, test_dl, test_buf, test_plr, dur);

  fclose(sender_config);

  LinkChangeEventData lc;
  lc.bw = 100;
  lc.bw_range = 90;
  lc.dl = 0.06;
  lc.dl_range = 0.05;
  lc.bf = 10000;
  lc.bf_range = 9000;
  lc.plr = 0.02;
  lc.plr_range = 0.02;
  lc.reset_queue = true;
  lc.change_interval = 5.0;
  lc.strata = 10;
  lc.cur_strata = 0;

  EventInfo lc_event(LINK_CHANGE, 0.0, 0, 0, 0.0);
  lc_event.data = (void*)(&lc);

  if (Options::Get("--sim-variable-link") != NULL) {
    simulator.EnqueueEvent(lc_event);
  }

  simulator.Run();
  simulator.Analyze();

  return 0;
}
