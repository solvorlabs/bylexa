import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  TextField,
  Card,
  CardContent,
  Grid,
  Rating,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  CircularProgress,
  Chip,
  Stack,
  Tabs,
  Tab,
  Fab,
  Tooltip
} from '@mui/material';
import { Search, Download, Code, Description, Add, Delete, Edit } from '@mui/icons-material';
import axios from 'axios';
import Config from '../config/Config';

const ScriptBrowser = () => {
  const [scripts, setScripts] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedScript, setSelectedScript] = useState(null);
  const [loading, setLoading] = useState(false);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [tab, setTab] = useState('browse');
  const [userScripts, setUserScripts] = useState([]);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [editScript, setEditScript] = useState(null);

  useEffect(() => {
    if (tab === 'my-scripts') {
      fetchUserScripts();
    }
  }, [tab]);

  useEffect(() => {
    fetchScripts();
  }, []);

  const fetchScripts = async (search = '') => {
    setLoading(true);
    try {
      const response = await axios.get(`${Config.backendUrl}/api/scripts/registry${search ? `?q=${search}` : ''}`);
      setScripts(response.data.scripts);
    } catch (error) {
      console.error('Error fetching scripts:', error);
    }
    setLoading(false);
  };

  const fetchUserScripts = async () => {
    try {
      const response = await axios.get(`${Config.backendUrl}/api/scripts/user`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      });
      setUserScripts(response.data.scripts);
    } catch (error) {
      console.error('Error fetching user scripts:', error);
    }
  };

  const handleSearch = (event) => {
    setSearchTerm(event.target.value);
    fetchScripts(event.target.value);
  };

  const handleScriptSelect = async (scriptId) => {
    try {
      const response = await axios.get(`${Config.backendUrl}/api/scripts/registry/${scriptId}`);
      setSelectedScript(response.data);
      setDialogOpen(true);
    } catch (error) {
      console.error('Error fetching script details:', error);
    }
  };

  const handleInstall = async (scriptId) => {
    try {
      const response = await axios.get(`${Config.backendUrl}/api/scripts/registry/${scriptId}/download`);
      console.log('Script installed:', response.data);
      // Add logic to handle successful installation
    } catch (error) {
      console.error('Error installing script:', error);
    }
  };

  const handleCreateScript = async (scriptData) => {
    try {
      await axios.post(
        `${Config.backendUrl}/api/scripts/registry`,
        scriptData,
        { headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } }
      );
      setCreateDialogOpen(false);
      fetchUserScripts();
    } catch (error) {
      console.error('Error creating script:', error);
    }
  };

  const handleDeleteScript = async (scriptId) => {
    if (window.confirm('Are you sure you want to delete this script?')) {
      try {
        await axios.delete(
          `${Config.backendUrl}/api/scripts/registry/${scriptId}`,
          { headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } }
        );
        fetchUserScripts();
      } catch (error) {
        console.error('Error deleting script:', error);
      }
    }
  };

  return (
    <div sx={{ py: 4 }} className='bg-black h-screen pt-20 px-10'>
      <br />
      <Typography variant="h4" gutterBottom className='text-white'>
        Script Browser
      </Typography>

      <Tabs value={tab} onChange={(e, newValue) => setTab(newValue)} sx={{ mb: 4 }}>
        <Tab value="browse" label="Browse Scripts" />
        <Tab value="my-scripts" label="My Scripts" />
      </Tabs>

      {tab === 'browse' ? (
        <>
          <TextField
            fullWidth
            variant="outlined"
            placeholder="Search scripts..."
            value={searchTerm}
            onChange={handleSearch}
            InputProps={{
              startAdornment: <Search color="action" sx={{ mr: 1 }} />
            }}
            sx={{ mb: 4 }}
          />

          {loading ? (
            <Box display="flex" justifyContent="center">
              <CircularProgress />
            </Box>
          ) : (
            <Grid container spacing={3}>
              {scripts.map((script) => (
                <Grid item xs={12} sm={6} md={4} key={script._id}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        {script.name}
                      </Typography>
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        {script.description}
                      </Typography>
                      <Stack direction="row" spacing={1} sx={{ mb: 2 }}>
                        {script.keywords.map((keyword) => (
                          <Chip key={keyword} label={keyword} size="small" />
                        ))}
                      </Stack>
                      <Box display="flex" alignItems="center" mb={2}>
                        <Rating value={script.rating} readOnly precision={0.5} />
                        <Typography variant="body2" color="text.secondary" sx={{ ml: 1 }}>
                          ({script.num_ratings})
                        </Typography>
                      </Box>
                      <Box display="flex" justifyContent="space-between">
                        <Button
                          startIcon={<Code />}
                          onClick={() => handleScriptSelect(script._id)}
                        >
                          Details
                        </Button>
                        <Button
                          startIcon={<Download />}
                          variant="contained"
                          onClick={() => handleInstall(script._id)}
                        >
                          Install
                        </Button>
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          )}
        </>
      ) : (
        <>
          <Box sx={{ mb: 4, display: 'flex', justifyContent: 'flex-end' }}>
            <Tooltip title="Create New Script">
              <Fab color="primary" onClick={() => setCreateDialogOpen(true)}>
                <Add />
              </Fab>
            </Tooltip>
          </Box>

          <Grid container spacing={3}>
            {userScripts.map((script) => (
              <Grid item xs={12} sm={6} md={4} key={script._id}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      {script.name}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      {script.description}
                    </Typography>
                    <Stack direction="row" spacing={1} sx={{ mb: 2 }}>
                      {script.keywords.map((keyword) => (
                        <Chip key={keyword} label={keyword} size="small" />
                      ))}
                    </Stack>
                    <Box display="flex" alignItems="center" mb={2}>
                      <Rating value={script.rating} readOnly precision={0.5} />
                      <Typography variant="body2" color="text.secondary" sx={{ ml: 1 }}>
                        ({script.num_ratings})
                      </Typography>
                    </Box>
                    <Box display="flex" justifyContent="space-between">
                      <Button
                        startIcon={<Edit />}
                        onClick={() => {
                          setEditScript(script);
                          setCreateDialogOpen(true);
                        }}
                      >
                        Edit
                      </Button>
                      <Button
                        startIcon={<Delete />}
                        color="error"
                        onClick={() => handleDeleteScript(script._id)}
                      >
                        Delete
                      </Button>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </>
      )}

      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="md" fullWidth>
        {selectedScript && (
          <>
            <DialogTitle>{selectedScript.name}</DialogTitle>
            <DialogContent>
              <Typography variant="body1" paragraph>
                {selectedScript.description}
              </Typography>
              <Typography variant="subtitle1" gutterBottom>
                Author: {selectedScript.author}
              </Typography>
              <Typography variant="subtitle1" gutterBottom>
                Version: {selectedScript.version}
              </Typography>
              <Typography variant="subtitle1" gutterBottom>
                Downloads: {selectedScript.downloads}
              </Typography>
              <Typography variant="subtitle1" gutterBottom>
                Requirements:
              </Typography>
              <Box component="pre" sx={{ bgcolor: 'grey.700', p: 2, borderRadius: 1 }}>
                {selectedScript.requirements.join('\n')}
              </Box>
            </DialogContent>
            <DialogActions>
              <Button onClick={() => setDialogOpen(false)}>Close</Button>
              <Button
                startIcon={<Download />}
                variant="contained"
                onClick={() => handleInstall(selectedScript._id)}
              >
                Install
              </Button>
            </DialogActions>
          </>
        )}
      </Dialog>

      <Dialog 
        open={createDialogOpen} 
        onClose={() => {
          setCreateDialogOpen(false);
          setEditScript(null);
        }}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          {editScript ? 'Edit Script' : 'Create New Script'}
        </DialogTitle>
        <DialogContent>
          <ScriptForm
            initialData={editScript}
            onSubmit={handleCreateScript}
            onCancel={() => {
              setCreateDialogOpen(false);
              setEditScript(null);
            }}
          />
        </DialogContent>
      </Dialog>
    </div>
  );
};

const ScriptForm = ({ initialData, onSubmit, onCancel }) => {
  const [formData, setFormData] = useState(initialData || {
    name: '',
    description: '',
    version: '1.0.0',
    source: '',
    requirements: [],
    keywords: []
  });

  return (
    <Box component="form" noValidate sx={{ mt: 2 }}>
      <TextField
        fullWidth
        label="Name"
        value={formData.name}
        onChange={(e) => setFormData({ ...formData, name: e.target.value })}
        margin="normal"
      />
      <TextField
        fullWidth
        label="Description"
        value={formData.description}
        onChange={(e) => setFormData({ ...formData, description: e.target.value })}
        margin="normal"
        multiline
        rows={3}
      />
      <TextField
        fullWidth
        label="Version"
        value={formData.version}
        onChange={(e) => setFormData({ ...formData, version: e.target.value })}
        margin="normal"
      />
      <TextField
        fullWidth
        label="Source Code"
        value={formData.source}
        onChange={(e) => setFormData({ ...formData, source: e.target.value })}
        margin="normal"
        multiline
        rows={10}
      />
      <TextField
        fullWidth
        label="Requirements (comma-separated)"
        value={formData.requirements.join(', ')}
        onChange={(e) => setFormData({ 
          ...formData, 
          requirements: e.target.value.split(',').map(r => r.trim()) 
        })}
        margin="normal"
      />
      <TextField
        fullWidth
        label="Keywords (comma-separated)"
        value={formData.keywords.join(', ')}
        onChange={(e) => setFormData({ 
          ...formData, 
          keywords: e.target.value.split(',').map(k => k.trim()) 
        })}
        margin="normal"
      />
      <Box sx={{ mt: 3, display: 'flex', justifyContent: 'flex-end', gap: 2 }}>
        <Button onClick={onCancel}>Cancel</Button>
        <Button 
          variant="contained" 
          onClick={() => onSubmit(formData)}
        >
          {initialData ? 'Update' : 'Create'}
        </Button>
      </Box>
    </Box>
  );
};

export default ScriptBrowser; 