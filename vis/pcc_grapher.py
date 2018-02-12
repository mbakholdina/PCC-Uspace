import os
import sys
import math
#import matplotlib as mpl
#mpl.use('Agg')
import matplotlib.pyplot as plt
import json
import numpy

from analysis.pcc_experiment_log import *
from analysis.pcc_filter import *
from analysis.pcc_log_summary import *

point_size = 6.0

if (len(sys.argv) == 1):
    print "usage: pcc_grapher.py <log_file_directory> <graph_json_file>"

log_files = os.listdir("./" + sys.argv[1])
experiment_logs = []
event_counts = []
for filename in log_files:
    log = PccExperimentLog("./" + sys.argv[1] + "/" + filename)
    if len(log.dict.keys()) > 0:
        experiment_logs.append(log)


graph_config = json.load(open(sys.argv[2]))
legend_param = graph_config["legend param"]
title = graph_config["title"] + " (by " + legend_param + ")"
event_type = graph_config["event"]
y_axis_names = graph_config["y-axis"]

for log in experiment_logs:
    log.apply_timeshift()

if "log filters" in graph_config.keys():
    pcc_filter = PccLogFilter(graph_config["log filters"])
    experiment_logs = pcc_filter.apply_filter(experiment_logs)

event_filters = None
if "event filters" in graph_config.keys():
    for event_filter_obj in graph_config["event filters"]:
        event_filter = PccEventFilter(event_filter_obj)
        for log in experiment_logs:
            event_filter.apply_filter(log)

    

for log in experiment_logs:
    if event_type not in log.get_event_types():
        experiment_logs.remove(log)

legend = []
for log in experiment_logs:
    legend.append(str(log.get_param(legend_param)))

if graph_config["type"] == "summary":
    legend = []
    log_groups = []
    group_filters = []
    if "groups" in graph_config.keys():
        group_filter_objs = graph_config["groups"]
        for group_filter_obj in group_filter_objs:
            print "Making group filter from " + str(group_filter_obj)
            group_filters.append(PccLogFilter(group_filter_obj))
    if len(group_filters) > 0:
        for group_filter in group_filters:
            log_groups.append(group_filter.apply_filter(experiment_logs))
            legend.append(group_filter.get_legend_label())
    else:
        log_groups = [experiment_logs]
    
    print "Found " + str(len(log_groups)) + " log groups!"
    for log_group in log_groups:
        print "Log group has " + str(len(log_group)) + " logs."
    log_group_x_values = []
    log_group_y_values = []
    for log_group in log_groups:
        experiment_logs = log_group
        x_axis_name = ""
        x_axis_values = []
        if "param" in graph_config["x-axis"].keys():
            x_axis_name = graph_config["x-axis"]["param"]
            for log in experiment_logs:
                x_axis_values.append(log.get_param(graph_config["x-axis"]))

        if "stat" in graph_config["x-axis"].keys():
            x_axis_obj = graph_config["x-axis"]
            for log in experiment_logs:
                log_summary = PccLogSummary(log)
                event_summary = log_summary.get_event_summary(graph_config["event"])
                x_axis_values.append(event_summary.get_summary_stat(
                    x_axis_obj["value"],
                    x_axis_obj["stat"]))
        
        y_axis_values = []
        y_axis_objs = graph_config["y-axis"]
        
        for i in range(0, len(y_axis_objs)):
            y_axis_values.append([])
            y_axis_obj = y_axis_objs[i]
            for log in experiment_logs:
                log_summary = PccLogSummary(log)
                event_summary = log_summary.get_event_summary(graph_config["event"])
                y_axis_values[i].append(event_summary.get_summary_stat(
                    y_axis_obj["value"],
                    y_axis_obj["stat"]))
        log_group_x_values.append(x_axis_values)
        log_group_y_values.append(y_axis_values)

    fig, axes = plt.subplots(len(y_axis_values), sharex=True)
    for i in range(0, len(y_axis_values)):
        handles = []
        y_axis_obj = y_axis_objs[i]
        y_axis_name = y_axis_obj["stat"] + " " + y_axis_obj["value"]
        for j in range(0, len(log_groups)):
            x_axis_values = log_group_x_values[j]
            y_axis_values = log_group_y_values[j]
            if len(y_axis_values) > 1:
                if x_axis_name == "Time":
                    handle, = axes[i].plot(x_axis_values, y_axis_values[i])
                else: 
                    handle = axes[i].scatter(x_axis_values, y_axis_values[i], s=point_size)
                handles.append(handle)
                axes[i].set_ylabel(y_axis_name)
            else:
                if x_axis_name == "Time":
                    handle, = axes.plot(x_axis_values, y_axis_values[i])
                else:
                    handle = axes.scatter(x_axis_values, y_axis_values[i], s=point_size)
                handles.append(handle)
                axes.set_ylabel(y_axis_name)
        plt.legend(handles, legend)
    
    if len(y_axis_names) > 1:
        axes[-1].set_xlabel(x_axis_name)
    else:
        axes.set_xlabel(x_axis_name)
    
    fig.suptitle(title)
    plt.show()
    #plt.savefig("graph.png")

if graph_config["type"] == "event":
    legend = []
    for log in experiment_logs:
        legend.append(str(log.get_param(legend_param)))
    x_axis_name = graph_config["x-axis"]

    avg_thpts = []
    loss_rates = []
    queue_lengths = []
    latencies = []
    x_axis_values = []
    y_axis_values = []
    for l in range(0, len(experiment_logs)):
        experiment_log = experiment_logs[l]
        this_log_x_axis_values = []
        this_log_y_axis_values = {}
        for y_axis_name in y_axis_names:
            this_log_y_axis_values[y_axis_name] = []
        for event in experiment_log.get_event_list(event_type):
            this_event = event
            this_log_x_axis_values.append(float(this_event[x_axis_name]))
            for k in this_log_y_axis_values.keys():
                this_log_y_axis_values[k].append(float(this_event[k]))
        x_axis_values.append(this_log_x_axis_values) 
        y_axis_values.append(this_log_y_axis_values) 
        

    fig, axes = plt.subplots(len(y_axis_values[0].keys()), sharex=True)
    for i in range(0, len(y_axis_names)):
        y_axis_name = y_axis_names[i]
        handles = []
        for j in range(0, len(experiment_logs)):
            #if y_axis_name == "Inverted Exponent Utility":
            #    y_axis_values[j][y_axis_name] = numpy.log10(y_axis_values[j][y_axis_name])
            if len(y_axis_names) > 1:
                if x_axis_name == "Time":
                    if "point event" in graph_config.keys():
                        graph_y_min = min(y_axis_values[j][y_axis_name])
                        point_event = graph_config["point event"]
                        point_event_x_values = []
                        point_event_y_values = []
                        k = 0
                        for event in experiment_logs[j].get_event_list(point_event):
                            print "Event " + str(k) + "/" + str(len(experiment_logs[j].get_event_list(point_event)))
                            k += 1
                            point_event_x_values.append(float(event["Time"]))
                            point_event_y_values.append(graph_y_min)
                        axes[i].scatter(point_event_x_values, point_event_y_values)
                    handle, = axes[i].plot(x_axis_values[j], y_axis_values[j][y_axis_name])
                else:
                    handle = axes[i].scatter(x_axis_values[j], y_axis_values[j][y_axis_name], s=point_size)
                handles.append(handle)
                plt.legend(handles, legend)
                axes[i].set_ylabel(y_axis_name)
            else:
                if x_axis_name == "Time":
                    if "point event" in graph_config.keys():
                        graph_y_min = min(y_axis_values[j][y_axis_name])
                        point_event = graph_config["point event"]
                        point_event_x_values = []
                        point_event_y_values = []
                        k = 0
                        for event in experiment_logs[j].get_event_list(point_event):
                            print "Event " + str(k) + "/" + str(len(experiment_logs[j].get_event_list(point_event)))
                            k += 1
                            point_event_x_values.append(float(event["Time"]))
                            point_event_y_values.append(graph_y_min)
                        axes[i].scatter(point_event_x_values, point_event_y_values)
                    handle, = axes.plot(x_axis_values[j], y_axis_values[j][y_axis_name])
                else:
                    handle = axes.scatter(x_axis_values[j], y_axis_values[j][y_axis_name], s=point_size)
                handles.append(handle)
                plt.legend(handles, legend)
                axes.set_ylabel(y_axis_name)
    
    if len(y_axis_names) > 1:
        axes[-1].set_xlabel(x_axis_name)
    else:
        axes.set_xlabel(x_axis_name)
    fig.suptitle(title)
    plt.show()
    #plt.savefig("graph.png")
