import React from 'react';
import { List, ListItem, ListItemText, Button } from '@mui/material';
import { Link } from 'react-router-dom';

const CourseList = ({ courses }) => {
  return (
    <List>
      {courses.map((course) => (
        <ListItem key={course._id}>
          <ListItemText
            primary={course.title}
            secondary={course.description}
          />
          <Button
            component={Link}
            to={`/courses/${course._id}`}
            variant="outlined"
          >
            Edit
          </Button>
        </ListItem>
      ))}
    </List>
  );
};

export default CourseList;
