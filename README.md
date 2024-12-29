# CommunereRAG

## Configuration

This application can be configured with environment variables.

You can create `.env` file in the root directory and place all
environment variables here. You can copy the `env.sample` file.
The only thing that needs changing is adding an openai api key. 
```bash
cp env.sample .env
```
## Docker

You can start the project with docker using this command:

```bash
docker compose build
docker compose -f docker-compose.yml -f deploy/docker-compose.dev.yml --project-directory . up -d
```

This command exposes the web application on port 8000.



## Project Architecture
- Project uses Taskiq to process the uploaded documents in background because it takes a long time to extract the embeddings, specially if pdf file is large.
- `/query` endpoint uses two agents. First, it retrieves relative data from Chromadb, then another agent refines the retrieved data for the final LLM answer.
- You can access api documentation from this url: `http://localhost:8000/api/docs`


## Sample logs
```json
{
    "_id": "67713bd7ed33147d209caa24",
    "query": "how can we minimize the maximum cooperative routing time in a truck-drone delivery scenario?",
    "response": "To minimize the maximum cooperative routing time in a truck-drone delivery scenario, several aspects can be optimized based on drone speed and endurance:\n\n1. **Drone Speed vs. Endurance**: Increasing drone speed (while reducing its endurance) can significantly reduce the travel time. This means drones can complete deliveries faster and reduce waiting times for trucks. For instance, increasing drone speed from 0.3 km/min to 1.8 km/min resulted in a reduction of travel time by around 32-33 minutes.\n\n2. **Balance Between Drone Capacity and Endurance**: As drone capacity decreases (meaning drones can carry fewer items but may have longer endurance), the best travel time improves. However, fulfillment rates may suffer, meaning fewer deliveries per trip. Therefore, it's important to find a balance that allows for both optimal travel time and a desirable fulfillment rate.\n\n3. **Optimize for High-Speed Drones**: While optimizing drone speed is effective, it's worth noting that fulfillment rates are not highly sensitive to changes in drone speed and endurance. Therefore, using high-speed drones can be beneficial to saving travel time without drastically affecting delivery capacity.\n\nBy focusing on these elements, the delivery system can lower the maximum cooperative routing time, enhancing the efficiency of the truck-drone delivery model.",
    "context": "\"Average best travel time” refers to the average value of the best travel time objective value obtained for each run. As the drone capacity decreases (drone endurance increases), the “Best fulfillment rate” and the “Average best fulfillment rate” both show a downward trend. For example, when the capacity dropped from 80 to 13 boxes (the endurance increased from 8 to 68 min), the “Best fulfillment rate” and the “Average best fulfillment rate” dropped by 107.39% and 90.19%, respectively.\n\nWhen the drone endurance increases (drone capacity decreases), the “Best travel time” and the “Average best travel time” also both show a downward trend. For example, when the endurance rises from 8 to 68 min (the capacity dropped from 80 to 13 boxes), the “Best travel time” and the “Average best travel time” dropped by 37.36 min and 45.68 min, respectively. Although the four items show a downward trend when the ratio of capacity and endurance drops, the two items on travel time objective are getting better, and the two items on fulfillment rate objective are getting worse. Compared with the improvement rate of the related “travel time” items, the related “fulfillment rate” items have a greater degree of deterioration. For example, when the capacity drops from 80 to 13 (endurance increases from 8 to 68 min), the drop rates of “Best fulfillment rate” and “Average best fulfillment rate” are 83.44% and 80.89%, while the improvement rates of “Best travel time” and “Average best travel time” are 14.91% and 16.32%, respectively. Therefore, we can see that when the drone capacity becomes smaller (the endurance becomes larger), the change in the fulfillment rate objective is more sensitive than the change in the travel time objective. In addition, it can be concluded that a larger capacity drone is beneficial to increase the fulfillment rate, but at the same time, it will also increase the travel time.\n\nDrone speed versus endurance: For the battery-powered drone, its speed would affect its endurance. We designed 6 speed/endurance combinations which are based on a fixed flight distance to analyze the impact of the trade-off between the drone endurance and capacity on the efficiencies of the truck-drone delivery model. The experiment results show the variation of the best value and average value of two objectives. The horizontal axis represents different speed and endurance combinations, and the two vertical axes represent travel time and fulfillment rate, respectively. As the speed increases (endurance decreases), the “Best travel time” and the “Average best travel time” show a significant downward trend. For example, when the speed increased from 0.3 km/minute to 1.8 km/minute (the endurance dropped from 60 to 10 min), the “Best travel time” and the “Average best travel time” dropped by 33 min and 32.85 min, respectively. A shorter delivery time of drone means a shorter waiting time for the truck, which is beneficial to shorten the travel time of truck-drone collaborative delivery. On the other hand, when the speed increases (endurance decreases), the “Best fulfillment rate” remained unchanged at 109.84% and the “Average best fulfillment rate” also stabilized at around 100% without significant changes. Therefore, the fulfillment rate objective is not sensitive to drone speed (endurance) changes. It can be concluded that the high-speed drone is beneficial to save the travel time of truck-drone delivery model.",
    "timestamp": "2024-12-29T12:08:55.933000",
    "duration": 18.370801210403442
  }
```

## Healthcheck
Project has a simple `/api/health` api to make sure project is up and running.
Also, every container in docker-compose has a healthcheck.

## Observability
Projects exposes Prometheus metrics (`http://localhost:8000/metrics`) for observability and monitoring purposes.

